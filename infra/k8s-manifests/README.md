# K8s Manifests

本项目以 Helm Chart 作为主要 Kubernetes 交付形式，位置为 `infra/helm/nekocafe`。

该目录用于说明原生 K8s 清单的归档位置：如果后续需要导出静态 Deployment、Service、Ingress、HPA 或 NetworkPolicy，可通过以下命令生成：

```bash
helm template nekocafe ../helm/nekocafe -f ../helm/nekocafe/values-dev.yaml > nekocafe-dev.yaml
helm template nekocafe ../helm/nekocafe -f ../helm/nekocafe/values-staging.yaml > nekocafe-staging.yaml
helm template nekocafe ../helm/nekocafe -f ../helm/nekocafe/values-prod.yaml > nekocafe-prod.yaml
```

课程实验三 D3-5 要求的 dev / staging / prod 差异化部署配置由 Helm values 文件表达。
