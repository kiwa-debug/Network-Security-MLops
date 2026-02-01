# EC2 Deployment Troubleshooting Guide

## Issue: Connection Refused on Port 8080

### Step 1: Check EC2 Security Group (MOST COMMON ISSUE)

1. Go to AWS Console → EC2 → Instances
2. Select your instance (54.242.208.216)
3. Click "Security" tab
4. Click on the Security Group name
5. Click "Edit inbound rules"
6. Verify there is a rule for port 8080:
   ```
   Type: Custom TCP
   Port Range: 8080
   Source: 0.0.0.0/0 (or your IP)
   ```
7. If not present, ADD IT and save

### Step 2: SSH into EC2 and Run Diagnostics

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@54.242.208.216

# Check if Docker container is running
docker ps

# Check container logs
docker logs networksecurity

# Check if port 8080 is listening
sudo netstat -tlnp | grep 8080

# Test local connection
curl http://localhost:8080/docs

# If container is not running, check why
docker ps -a
docker logs networksecurity --tail 200
```

### Step 3: Check GitHub Actions Logs

Go to your GitHub repository:
1. Click "Actions" tab
2. Click on the latest workflow run
3. Look at the "Check container status and logs" step
4. Check for any errors in the container logs

### Step 4: Common Issues and Solutions

#### Issue: Container exits immediately
**Solution:** Check MongoDB connection string in GitHub Secrets
- Go to Settings → Secrets and variables → Actions
- Verify `MONGODB_URL_KEY` is set correctly

#### Issue: Port already in use
**Solution:** Kill old containers
```bash
docker stop networksecurity
docker rm networksecurity
```

#### Issue: Out of disk space
**Solution:** Clean up Docker
```bash
docker system prune -af --volumes
```

#### Issue: Application crashes on startup
**Solution:** Check container logs
```bash
docker logs networksecurity --tail 200
```

### Step 5: Manual Container Start (for testing)

```bash
# Pull the image
docker pull YOUR_ECR_URI/YOUR_REPO:latest

# Run manually with all environment variables
docker run -d -p 8080:8080 --name=networksecurity \
  -e 'AWS_ACCESS_KEY_ID=YOUR_KEY' \
  -e 'AWS_SECRET_ACCESS_KEY=YOUR_SECRET' \
  -e 'AWS_REGION=us-east-1' \
  -e 'MONGODB_URL_KEY=mongodb+srv://...' \
  YOUR_ECR_URI/YOUR_REPO:latest

# Check logs
docker logs -f networksecurity
```

### Required GitHub Secrets

Make sure these are configured in GitHub:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REPOSITORY_NAME`
- `AWS_ECR_LOGIN_URI`
- `MONGODB_URL_KEY` (with password URL-encoded: Kiwa%40183)

### Testing from Local Machine

Once the Security Group is configured:
```bash
# Test from your machine
curl http://54.242.208.216:8080/docs
```

### If Nothing Works

1. Stop the GitHub Actions runner
2. SSH into EC2
3. Run the debug script:
   ```bash
   bash debug_ec2.sh
   ```
4. Share the output for further debugging
