# REPERMON

## The AIOps CI/CD Performance Operator

### How to run pre-commit
Run the pre-commit you need to run the command below:

```bash
pre-commit run --all-files
```

Or the corresponding dagger function:

```bash
dagger call pre-commmit
```

### Dagger functions

```bash
❯  dagger functions

Name           Description
cluster        Returns a service with the created cluster
get-config     Returns the kubeconfig for the created cluster
kns            Returns a k9s container with the created cluster
pre-commit     Runs pre-commit for a given source (git or local)
test-cluster   Tests the manifests in the source directory
```

> [!NOTE]
> All dagger functions can be ran by specifying a commit sha
> Example:
> ```bash
> dagger call --commit <COMMIT-SHA> <FUNCTION-NAME>
> ```
