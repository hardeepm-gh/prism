# Experiment 5: Default SA fails

## What
Pod without serviceAccountName uses default SA
default SA can get secrets? NO

## Learning
If app needs secrets/configmaps, must specify serviceAccountName in Deployment
Otherwise it uses default SA with no permissions and fails
