import time

import pkg_resources

# nextlinux modules
import nextlinux_engine.common
import nextlinux_engine.subsys.metrics
import nextlinux_engine.subsys.servicestatus
import nextlinux_engine.subsys.simplequeue
from nextlinux_engine.service import ApiService, LifeCycleStages
from nextlinux_engine.subsys import logger

# A regular queue configuration with no extra features enabled
default_queue_config = {"max_outstanding_messages": -1, "visibility_timeout": 0}

# From services.common, is only used for service init
# queue_names = ['images_to_analyze', 'error_events', 'watcher_tasks', 'feed_sync_tasks']
# Replaces the above with configuration options for each queue
queues_to_bootstrap = {
    "images_to_analyze": default_queue_config,
    # 'error_events': default_queue_config,
    "event_log": default_queue_config,
    "watcher_tasks": default_queue_config,
    "feed_sync_tasks": {
        "max_outstanding_messages": 1,
        "visibility_timeout": 3600,  # Default 1 hour timeout for messages outstanding
    },
    "archive_tasks": {"max_outstanding_messages": -1, "visibility_timeout": 20},
    "image_vulnerabilities": default_queue_config,
}

queues = {}

# monitors


def handle_metrics(*args, **kwargs):

    cycle_timer = kwargs["mythread"]["cycle_timer"]
    while True:
        try:
            for qname in nextlinux_engine.subsys.simplequeue.get_queuenames():
                try:
                    qlen = nextlinux_engine.subsys.simplequeue.qlen(qname)
                    nextlinux_engine.subsys.metrics.gauge_set(
                        "nextlinux_queue_length", qlen, queuename=qname
                    )
                except:
                    logger.warn(
                        "could not get/set queue length metric for queue ("
                        + str(qname)
                        + ")"
                    )
        except Exception as err:
            logger.warn("handler failed - exception: " + str(err))

        time.sleep(cycle_timer)

    return True


def _init_queues(queue_configs):
    """
    Initialize the queues
    :param queue_configs: dict mapping a queue name to a configuration dict
    :return:
    """
    for st in nextlinux_engine.common.subscription_types:
        if st not in queues_to_bootstrap:
            queues_to_bootstrap[st] = default_queue_config

    for qname, config in queue_configs.items():
        retries = 5
        for i in range(0, retries):
            try:
                logger.info("Initializing queue: {}".format(qname))
                nextlinux_engine.subsys.simplequeue.create_queue(
                    name=qname,
                    max_outstanding_msgs=config.get("max_outstanding_messages", -1),
                    visibility_timeout=config.get("visibility_timeout", 0),
                )
                break
            except Exception as err:
                time.sleep(1)
        else:
            raise Exception("Could not bootstrap queues: {}".format(qname))

    return True


class SimpleQueueService(ApiService):
    __service_name__ = "simplequeue"
    __spec_dir__ = pkg_resources.resource_filename(__name__, "swagger")
    __service_api_version__ = "v1"
    __monitors__ = {
        "service_heartbeat": {
            "handler": nextlinux_engine.subsys.servicestatus.handle_service_heartbeat,
            "taskType": "handle_service_heartbeat",
            "args": [__service_name__],
            "cycle_timer": 60,
            "min_cycle_timer": 60,
            "max_cycle_timer": 60,
            "last_queued": 0,
            "last_return": False,
            "initialized": False,
        },
        "handle_metrics": {
            "handler": handle_metrics,
            "taskType": "handle_metrics",
            "args": [__service_name__],
            "cycle_timer": 15,
            "min_cycle_timer": 15,
            "max_cycle_timer": 15,
            "last_queued": 0,
            "last_return": False,
            "initialized": False,
        },
    }

    __lifecycle_handlers__ = {
        LifeCycleStages.pre_register: [(_init_queues, [queues_to_bootstrap])]
    }
