1. Test Django
```
python manage.py test
```

2. Build container (DigitalOcean example)
```
docker build -f Dockerfile \
    -t registry.digitalocean.com/django-tracer/django-tracer:latest \
    -t registry.digitalocean.com/django-tracer/django-tracer:v1 \
    .
```

3. Push container to DigitalOcean Container Registry
```
docker push registry.digitalocean.com/django-tracer/django-tracer --all-tags
```

4. Update secrets
```
kubectl delete secret django-k8s-web-prod-env
kubectl create secret generic django-k8s-web-prod-env --from-env-file=.env.prod
```

5. Update deployment
```
kubectl apply -f k8s/app/django-k8s-web.yaml
```

6. Wait for Rollout to complete
```
kubectl rollout status deployment/django-k8s-web-deployment
```

7. Migrate database
```
export SINGLE_POD_NAME=$(kubectl get pods -l app=django-k8s-web-deployment -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $SINGLE_POD_NAME -- bash /app/migrate.sh
```