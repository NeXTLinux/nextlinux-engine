# navigate to the Git repository
cd ./

# replace all occurrences of 'old_text' with 'new_text' in all file names
for file in $(git ls-files "*old_text*"); do
  newfile=$(echo $file | sed "s/ANCHORE/NEXTLINUX/g")
  git mv "$file" "$newfile"
done
