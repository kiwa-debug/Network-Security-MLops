# GitHub Actions Deployment Checklist

## ✅ Pre-Deployment Setup

### 1. AWS ECR Repository Setup
- [ ] ECR repository created in AWS
- [ ] Repository name matches `ECR_REPOSITORY_NAME` secret
- [ ] Repository is in the correct region

**How to create ECR repository:**
```bash
aws ecr create-repository --repository-name network-security --region us-east-1
```

### 2. GitHub Secrets Configuration
Go to: Repository → Settings → Secrets and variables → Actions

Required secrets:
- [ ] `AWS_ACCESS_KEY_ID` - Your AWS access key
- [ ] `AWS_SECRET_ACCESS_KEY` - Your AWS secret key  
- [ ] `AWS_REGION` - e.g., `us-east-1`
- [ ] `ECR_REPOSITORY_NAME` - e.g., `network-security`
- [ ] `AWS_ECR_LOGIN_URI` - e.g., `123456789.dkr.ecr.us-east-1.amazonaws.com`
- [ ] `MONGODB_URL_KEY` - MongoDB connection string with URL-encoded password

**MongoDB URL format:**
```
mongodb+srv://kirtish:Kiwa%40183@cluster0.mohrvux.mongodb.net/?appName=Cluster0
```
(Note: `@` symbol in password is encoded as `%40`)

### 3. Self-Hosted Runner Setup
- [ ] EC2 instance is running
- [ ] GitHub Actions runner is installed and running
- [ ] Runner is registered to your repository
- [ ] Docker is installed on EC2
- [ ] AWS CLI is installed on EC2

**Check runner status:**
Go to: Repository → Settings → Actions → Runners

### 4. EC2 Security Group Configuration
- [ ] Inbound rule for port 8080 is configured
- [ ] Source: `0.0.0.0/0` (or your specific IP)
- [ ] Protocol: TCP
- [ ] Port Range: 8080

### 5. AWS IAM Permissions
Your AWS user/role needs these permissions:
- [ ] ECR push/pull permissions
- [ ] ECR describe-images permission
- [ ] ECR GetAuthorizationToken permission

**Minimal IAM policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:DescribeImages"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🔍 Troubleshooting Checklist

### If "Pull latest images" fails:

1. **Check if ECR repository exists:**
```bash
aws ecr describe-repositories --region us-east-1
```

2. **Check if image exists in ECR:**
```bash
aws ecr describe-images --repository-name network-security --region us-east-1
```

3. **Verify ECR URI format:**
- Should be: `ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com`
- Example: `123456789.dkr.ecr.us-east-1.amazonaws.com`

4. **Check GitHub Actions logs:**
- Look at "Build, tag, and push image to Amazon ECR" step
- Verify it completed successfully
- Check for any Docker build errors

5. **Verify AWS credentials:**
```bash
# On your EC2 instance
aws sts get-caller-identity
```

### If Docker build fails:

1. **Check Dockerfile syntax**
2. **Verify base image exists:** `python:3.12-slim`
3. **Check requirements.txt** for any problematic dependencies
4. **Look for disk space issues** in GitHub Actions logs

### If container fails to start:

1. **SSH into EC2:**
```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```

2. **Check container logs:**
```bash
docker logs networksecurity
```

3. **Common issues:**
- MongoDB connection failure → Check MONGODB_URL_KEY secret
- Missing environment variables → Verify all secrets are set
- Port conflict → Check if port 8080 is already in use

---

## 🚀 Deployment Steps

### First Time Deployment:

1. **Create ECR repository** (if not exists)
2. **Configure all GitHub secrets**
3. **Set up EC2 Security Group** for port 8080
4. **Commit and push changes** to main branch
5. **Monitor GitHub Actions** workflow
6. **Check logs** at each step
7. **Verify deployment** by accessing `http://YOUR_EC2_IP:8080/docs`

### Subsequent Deployments:

1. **Make code changes**
2. **Commit and push** to main branch
3. **GitHub Actions automatically:**
   - Builds new Docker image
   - Pushes to ECR
   - Deploys to EC2
   - Cleans up old containers

---

## 📝 Quick Reference

### Get ECR Login URI:
```bash
aws ecr describe-repositories --repository-name network-security --region us-east-1 --query 'repositories[0].repositoryUri' --output text
```
Then remove the repository name from the end to get just the URI.

### Manual Docker Pull (for testing):
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker pull YOUR_ECR_URI/network-security:latest
```

### Check GitHub Actions Status:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

### Access Deployed Application:
```
http://YOUR_EC2_IP:8080/docs
```
