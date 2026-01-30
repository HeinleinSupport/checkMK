---
name: gerrit
description: Interact with Gerrit code review to list changes and improve them
---

# When asked to improve a Gerrit change:

1. Fetch the current state from Gerrit

`gerrit-change-log HEAD`

2. In case a Verified -1 is reported, fetch the Jenkins job results using the jenkins skill
3. For each failed stage, fetch the details of the triggered stage job

# When asked for the list of open Gerrit changes

```
# List all your open changes
gerrit-change-log --list

# Find changes needing attention (negative score)
gerrit-change-log --list | grep ':-'
```

# In case the command gerrit-change-log is missing

Ask the user to clone the zeug_cmk git repository and add it to their PATH.
See also: https://wiki.lan.checkmk.net/x/4zBSCQ
