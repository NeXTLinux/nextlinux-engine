"""
API Handlers for /policies routes

"""

import connexion
import hashlib
import json

import nextlinux_engine.apis
import nextlinux_engine.common
import nextlinux_engine.common.helpers
from nextlinux_engine import db
import nextlinux_engine.services.catalog.catalog_impl
from nextlinux_engine.subsys import logger
import nextlinux_engine.configuration.localconfig
import nextlinux_engine.subsys.servicestatus
import nextlinux_engine.utils

from nextlinux_engine.db import db_policybundle, db_policyeval
from nextlinux_engine.subsys import object_store
from nextlinux_engine.apis.authorization import get_authorizer, INTERNAL_SERVICE_ALLOWED

import nextlinux_engine.subsys.events

authorizer = get_authorizer()


@authorizer.requires_account(with_types=INTERNAL_SERVICE_ALLOWED)
def list_policies(active=None):
    """
    GET /policies?active=true|false
    :return:
    """

    # set up the filter based on input
    try:

        object_storage_mgr = object_store.get_manager()
        request_inputs = nextlinux_engine.apis.do_request_prep(
            connexion.request, default_params={}
        )
        user_id = request_inputs["userId"]

        with db.session_scope() as dbsession:
            if active is not None:
                records = db_policybundle.get_byfilter(
                    user_id, session=dbsession, active=active
                )
            else:
                records = db_policybundle.get_byfilter(user_id, session=dbsession)

        if records:
            for record in records:
                record["policybundle"] = {}
                try:
                    policybundle = object_storage_mgr.get_document(
                        user_id, "policy_bundles", record["policyId"]
                    )
                    if policybundle:
                        record["policybundle"] = policybundle

                        record["policybundlemeta"] = {}
                        meta = object_storage_mgr.get_document_meta(
                            user_id, "policy_bundles", record["policyId"]
                        )
                        if meta:
                            record["policybundlemeta"] = meta

                except Exception as err:
                    logger.warn(
                        "failed to fetch policy bundle from archive - exception: "
                        + str(err)
                    )
                    raise nextlinux_engine.common.helpers.make_nextlinux_exception(
                        err,
                        input_message="failed to fetch policy bundle from archive",
                        input_httpcode=500,
                    )
        else:
            records = []

        return records, 200
    except Exception as err:
        logger.exception("Uncaught exception")
        return str(err), 500


@authorizer.requires_account(with_types=INTERNAL_SERVICE_ALLOWED)
def get_policy(policyId):
    """
    GET /policies/{policyId}

    :param policyId:
    :return:
    """
    try:
        object_storage_mgr = object_store.get_manager()

        request_inputs = nextlinux_engine.apis.do_request_prep(
            connexion.request, default_params={}
        )
        user_id = request_inputs["userId"]

        with db.session_scope() as dbsession:
            record = db_policybundle.get(user_id, policyId=policyId, session=dbsession)

        if record:
            record["policybundle"] = {}
            try:
                policybundle = object_storage_mgr.get_document(
                    user_id, "policy_bundles", record["policyId"]
                )
                if policybundle:
                    record["policybundle"] = policybundle

                    record["policybundlemeta"] = {}
                    meta = object_storage_mgr.get_document_meta(
                        user_id, "policy_bundles", record["policyId"]
                    )
                    if meta:
                        record["policybundlemeta"] = meta

            except Exception as err:
                logger.warn(
                    "failed to fetch policy bundle from archive - exception: "
                    + str(err)
                )
                raise nextlinux_engine.common.helpers.make_nextlinux_exception(
                    err,
                    input_message="failed to fetch policy bundle from archive",
                    input_httpcode=500,
                )
            return record, 200
        else:
            return (
                nextlinux_engine.common.helpers.make_response_error(
                    "Policy bundle {} not found in DB".format(policyId), in_httpcode=404
                ),
                404,
            )
    except Exception as err:
        logger.exception("Uncaught exception")
        return str(err), 500


@authorizer.requires_account(with_types=INTERNAL_SERVICE_ALLOWED)
def update_policy(policyId, bodycontent):
    """
    PUT /policies/{policyId}

    Updates a policy

    :param user_context:
    :param policyId:
    :param policy_content:
    :return:
    """
    try:
        request_inputs = nextlinux_engine.apis.do_request_prep(
            connexion.request, default_params={}
        )
        user_id = request_inputs["userId"]
        bundle_policyId = bodycontent.get("policyId")
        active = bodycontent.get("active", False)

        if not bundle_policyId:
            raise Exception(
                "must include 'policyId' in the json payload for this operation"
            )

        if policyId != bundle_policyId:
            raise Exception(
                "Id mismatch between route and bundle content. {} != {}".format(
                    policyId, bundle_policyId
                )
            )

        policybundle = bodycontent.get("policybundle")

        with db.session_scope() as dbsession:
            record = db_policybundle.get(user_id, policyId, session=dbsession)
            if not record:
                return (
                    nextlinux_engine.common.helpers.make_response_error(
                        "Existing policyId not found to update", in_httpcode=404
                    ),
                    404,
                )

            return save_policy(user_id, policyId, active, policybundle, dbsession), 200

    except Exception as err:
        logger.exception("Uncaught exception")
        return str(err), 500


@authorizer.requires_account(with_types=INTERNAL_SERVICE_ALLOWED)
def add_policy(bodycontent):
    """
    POST /policies

    Create a new policy document

    :param user_context:
    :param policy_bundle_content:
    :return:
    """

    try:
        request_inputs = nextlinux_engine.apis.do_request_prep(
            connexion.request, default_params={}
        )
        user_id = request_inputs["userId"]

        policyId = bodycontent.get("policyId")
        policybundle = bodycontent.get("policybundle")
        active = bodycontent.get("active", False)

        if not policyId:
            return (
                nextlinux_engine.common.helpers.make_response_error(
                    "policyId is required field in json body", in_httpcode=400
                ),
                400,
            )

        with db.session_scope() as dbsession:
            return save_policy(user_id, policyId, active, policybundle, dbsession), 200

    except Exception as err:
        logger.exception("Uncaught exception")
        return str(err), 500


@authorizer.requires_account(with_types=INTERNAL_SERVICE_ALLOWED)
def delete_policy(policyId, cleanup_evals=False):
    """
    DELETE /policies/{policyId}?cleanup_evals=true|false

    :param user_context:
    :param policyId:
    :param cleanup_evals:
    :return:
    """

    httpcode = 200
    return_object = True

    try:
        with db.session_scope() as dbsession:
            request_inputs = nextlinux_engine.apis.do_request_prep(
                connexion.request, default_params={}
            )
            user_id = request_inputs["userId"]

            policy_record = db_policybundle.get(user_id, policyId, session=dbsession)

            if policy_record:
                rc, httpcode = do_policy_delete(
                    user_id,
                    policy_record,
                    dbsession,
                    force=True,
                    cleanup_evals=cleanup_evals,
                )
                if httpcode not in list(range(200, 299)):
                    raise Exception(str(rc))

            return return_object, httpcode
    except Exception as ex:
        logger.exception("Uncaught exception")
        raise ex


def save_policy(user_id, policyId, active, policy_bundle, dbsession):
    """
    Do the save, outside the context of an api call itself.


    :param user_id: str - requesting usera
    :param policyId: str - the id for policy
    :param active: boolean - is active or not
    :param policy_bundle: dict - bundle content
    :return:
    """

    try:
        active_record = db_policybundle.get_active_policy(user_id, session=dbsession)
        last_active_policyId = active_record.get("policyId", None)
    except:
        last_active_policyId = None

    object_store_mgr = object_store.get_manager()

    # if update is to currently active bundle, check if the bundle content is to be changed
    if last_active_policyId == policyId:
        try:
            last_policy_bundle_content = object_store_mgr.get_document(
                user_id, "policy_bundles", policyId
            )
            if last_policy_bundle_content:
                last_policy_bundle_digest = hashlib.sha256(
                    nextlinux_engine.utils.ensure_bytes(
                        json.dumps(last_policy_bundle_content, sort_keys=True)
                    )
                ).hexdigest()
                new_policy_bundle_digest = hashlib.sha256(
                    nextlinux_engine.utils.ensure_bytes(
                        json.dumps(policy_bundle, sort_keys=True)
                    )
                ).hexdigest()
                if last_policy_bundle_digest != new_policy_bundle_digest:
                    event = nextlinux_engine.subsys.events.ActivePolicyBundleContentChanged(
                        user_id=user_id,
                        data={
                            "policy_id": policyId,
                            "last_policy_bundle_digest": last_policy_bundle_digest,
                            "current_policy_bundle_digest": new_policy_bundle_digest,
                        },
                    )
                    try:
                        nextlinux_engine.services.catalog.catalog_impl.add_event(
                            event, dbsession
                        )
                    except:
                        logger.warn(
                            "Ignoring error creating active policy content change event"
                        )
        except Exception as err:
            logger.warn(
                "Could not evaluate bundle content different on save for active bundle - exception: {}".format(
                    err
                )
            )

    try:
        if object_store_mgr.put_document(
            user_id, "policy_bundles", policyId, policy_bundle
        ):
            rc = db_policybundle.update(
                policyId, user_id, active, policy_bundle, session=dbsession
            )
        else:
            rc = False
    except Exception as err:
        raise nextlinux_engine.common.helpers.make_nextlinux_exception(
            err,
            input_message="cannot add policy, failed to update archive/DB",
            input_httpcode=500,
        )
    if not rc:
        raise Exception("DB update failed")
    else:
        if active:
            try:
                rc = db_policybundle.set_active_policy(
                    policyId, user_id, session=dbsession
                )
                if rc:
                    if policyId != last_active_policyId:
                        # a new policy is now active
                        event = (
                            nextlinux_engine.subsys.events.ActivePolicyBundleIdChanged(
                                user_id=user_id,
                                data={
                                    "last_policy_bundle_id": last_active_policyId,
                                    "current_policy_bundle_id": policyId,
                                },
                            )
                        )
                        try:
                            nextlinux_engine.services.catalog.catalog_impl.add_event(
                                event, dbsession
                            )
                        except:
                            logger.warn(
                                "Ignoring error creating active policy id change event"
                            )

            except Exception as err:
                raise Exception(
                    "could not set policy as active - exception: " + str(err)
                )

        record = db_policybundle.get(user_id, policyId, session=dbsession)
        record["policybundle"] = policy_bundle

        return record


def do_policy_delete(
    userId, policy_record, dbsession, cleanup_evals=False, force=False
):
    """
    Non-api delete of policy

    :param userId:
    :param policy_record:
    :param dbsession:
    :param cleanup_evals:
    :param force:
    :return:
    """
    return_object = False
    httpcode = 500

    try:
        policyId = policy_record["policyId"]

        rc = db_policybundle.delete(policyId, userId, session=dbsession)
        if not rc:
            httpcode = 500
            raise Exception("DB delete of policyId (" + str(policyId) + ") failed")
        else:
            if cleanup_evals:
                dbfilter = {"policyId": policyId}
                eval_records = db_policyeval.tsget_byfilter(
                    userId, session=dbsession, **dbfilter
                )
                for eval_record in eval_records:
                    db_policyeval.delete_record(eval_record, session=dbsession)

        return_object = True
        httpcode = 200
    except Exception as err:
        return_object = str(err)

    return return_object, httpcode
