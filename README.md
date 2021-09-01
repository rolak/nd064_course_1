# nd064_C1


Get argo password
```
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Docker tags
```
https://github.com/docker/build-push-action/blob/master/docs/advanced/tags-labels.md
```