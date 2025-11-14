# 🔧 Troubleshooting Guide

## Overview
This guide provides comprehensive troubleshooting steps for each component in the AB3 Hotel Booking System architecture. Use this guide to diagnose and resolve common issues.

## 🚨 Critical Issues - Immediate Actions

### System-Wide Failures
- **Check AWS Service Health**: [AWS Service Health Dashboard](https://health.aws.amazon.com/health/home)
- **Verify CloudFormation Stack Status**: `aws cloudformation describe-stacks --stack-name ab3-full-stack`
- **Check IAM Permissions**: Ensure service roles have required policies attached

---

## 🛡️ Lambda Functions

### X-Ray Extraction Function (`ab3-xray-XRayExtractionFunction`)

#### Common Issues

**Issue: Lambda function timeout (15 minutes)**
```bash
# Check function configuration
aws lambda get-function-configuration --function-name ab3-xray-XRayExtractionFunction

# Solution: Increase timeout or optimize batch size
aws lambda update-function-configuration \
  --function-name ab3-xray-XRayExtractionFunction \
  --timeout 900
```

**Issue: X-Ray API throttling**
```bash
# Check CloudWatch logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/ab3-xray-XRayExtractionFunction \
  --filter-pattern "ThrottlingException"

# Solution: Implement exponential backoff (check lambda_function.py)
```

**Issue: S3 permissions error**
```bash
# Verify Lambda execution role has S3 permissions
aws iam get-role-policy \
  --role-name ab3-xray-extraction-role \
  --policy-name S3AccessPolicy

# Check S3 bucket policy
aws s3api get-bucket-policy --bucket ab3-xray-data-YOUR-ACCOUNT-ID
```

#### Diagnostics
```bash
# View recent invocations
aws lambda get-function --function-name ab3-xray-XRayExtractionFunction

# Check error metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=ab3-xray-XRayExtractionFunction \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Sum
```

### Hotel Trace Generator Function (`lambda-generator-HotelTraceGeneratorFunction`)

#### Common Issues

**Issue: Synthetic traces not appearing in X-Ray**
```bash
# Check if X-Ray tracing is enabled
aws lambda get-function-configuration \
  --function-name lambda-generator-HotelTraceGeneratorFunction \
  --query 'TracingConfig'

# Enable X-Ray tracing if disabled
aws lambda put-function-configuration \
  --function-name lambda-generator-HotelTraceGeneratorFunction \
  --tracing-config Mode=Active
```

**Issue: Memory limitations**
```bash
# Check memory usage in CloudWatch
aws logs filter-log-events \
  --log-group-name /aws/lambda/lambda-generator-HotelTraceGeneratorFunction \
  --filter-pattern "REPORT"

# Increase memory if needed
aws lambda update-function-configuration \
  --function-name lambda-generator-HotelTraceGeneratorFunction \
  --memory-size 512
```

---

## 🌐 API Gateway (`HotelTracingAPI`)

### Common Issues

**Issue: 403 Forbidden responses**
```bash
# Check WAF rules
aws wafv2 list-web-acls --scope REGIONAL

# Review API Gateway authorizer
aws apigateway get-authorizers --rest-api-id YOUR-API-ID

# Test Cognito token
aws cognito-idp initiate-auth \
  --client-id YOUR-CLIENT-ID \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=testuser,PASSWORD=password
```

**Issue: High latency**
```bash
# Check API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Latency \
  --dimensions Name=ApiName,Value=HotelTracingAPI \
  --start-time $(date -d '1 hour ago' -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Average,Maximum
```

**Issue: CORS errors**
```bash
# Verify CORS configuration
aws apigateway get-method \
  --rest-api-id YOUR-API-ID \
  --resource-id YOUR-RESOURCE-ID \
  --http-method OPTIONS
```

### Diagnostics
```bash
# Enable detailed CloudWatch metrics
aws apigateway put-stage \
  --rest-api-id YOUR-API-ID \
  --stage-name prod \
  --patch-ops op=replace,path=/metricsEnabled,value=true

# Check access logs
aws logs describe-log-groups --log-group-name-prefix API-Gateway-Execution-Logs
```

---

## 🔄 Glue ETL Jobs

### Prep-Trace-Data-for-TCO_TBM

#### Common Issues

**Issue: Job fails with out-of-memory error**
```bash
# Check job configuration
aws glue get-job --job-name Prep-Trace-Data-for-TCO_TBM

# Increase DPU allocation
aws glue update-job \
  --job-name Prep-Trace-Data-for-TCO_TBM \
  --job-update '{
    "AllocatedCapacity": 10,
    "MaxCapacity": 10
  }'
```

**Issue: S3 data not found**
```bash
# Verify S3 data exists
aws s3 ls s3://ab3-xray-data-YOUR-ACCOUNT-ID/traces/ --recursive

# Check Glue job permissions
aws iam list-attached-role-policies --role-name ab3-glue-service-role
```

**Issue: Schema evolution errors**
```bash
# Check Glue Data Catalog
aws glue get-table --database-name ab3_database --name xray_traces

# Update table schema if needed
aws glue update-table \
  --database-name ab3_database \
  --table-input file://updated-table-schema.json
```

### ETL-Final-With-Athena-Only

#### Common Issues

**Issue: Athena query timeout**
```bash
# Check Athena query execution
aws athena list-query-executions --max-results 10

# Optimize query by partitioning
# Add partition columns to your table schema
```

**Issue: Insufficient Athena service limits**
```bash
# Check service quotas
aws service-quotas get-service-quota \
  --service-code athena \
  --quota-code L-76A4281B  # Concurrent DML queries

# Request quota increase if needed
```

### CRS-RMS-and-Hotels

#### Common Issues

**Issue: Redshift connection timeout**
```bash
# Verify VPC security group rules
aws ec2 describe-security-groups \
  --filters Name=group-name,Values=ab3-redshift-sg

# Check Redshift cluster status
aws redshift describe-clusters --cluster-identifier tco-tbm-ab3
```

### Diagnostics for All Glue Jobs
```bash
# Check recent job runs
aws glue get-job-runs --job-name JOB-NAME --max-results 5

# View detailed logs
aws logs filter-log-events \
  --log-group-name /aws-glue/jobs/logs-v2 \
  --filter-pattern "JOB-NAME"

# Monitor job metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Glue \
  --metric-name glue.driver.aggregate.numCompletedTasks \
  --dimensions Name=JobName,Value=JOB-NAME \
  --start-time $(date -d '1 hour ago' -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Sum
```

---

## 🗄️ Redshift Cluster (`tco-tbm-ab3`)

### Common Issues

**Issue: Connection refused**
```bash
# Check cluster status
aws redshift describe-clusters --cluster-identifier tco-tbm-ab3

# Verify security group allows connections
aws ec2 describe-security-groups \
  --group-ids sg-YOUR-SECURITY-GROUP-ID

# Test connection
psql -h tco-tbm-ab3.CLUSTER-ID.REGION.redshift.amazonaws.com \
     -p 5439 -U admin -d dev
```

**Issue: Query performance degradation**
```bash
# Check cluster metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Redshift \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterIdentifier,Value=tco-tbm-ab3 \
  --start-time $(date -d '1 hour ago' -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Average,Maximum

# Analyze query performance
# Connect to Redshift and run:
# SELECT * FROM stl_query WHERE starttime > CURRENT_TIMESTAMP - INTERVAL '1 hour';
```

**Issue: Storage full**
```bash
# Check storage metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Redshift \
  --metric-name PercentageDiskSpaceUsed \
  --dimensions Name=ClusterIdentifier,Value=tco-tbm-ab3 \
  --start-time $(date -d '24 hours ago' -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 3600 \
  --statistics Maximum

# Resize cluster if needed
aws redshift modify-cluster \
  --cluster-identifier tco-tbm-ab3 \
  --node-type dc2.large \
  --number-of-nodes 3
```

### Maintenance Tasks
```sql
-- Run in Redshift Query Editor
-- Analyze table statistics
ANALYZE;

-- Vacuum tables to reclaim space
VACUUM;

-- Check table skew
SELECT
    schemaname,
    tablename,
    max(size) as max_size,
    min(size) as min_size,
    (max(size) - min(size)) as skew
FROM svv_table_info
GROUP BY schemaname, tablename
ORDER BY skew DESC;
```

---

## 📱 Amplify App

### Common Issues

**Issue: Build failures**
```bash
# Check build status
aws amplify list-jobs --app-id YOUR-APP-ID --branch-name main

# View build logs
aws amplify get-job \
  --app-id YOUR-APP-ID \
  --branch-name main \
  --job-id YOUR-JOB-ID

# Common fixes:
# 1. Update Node.js version in build settings
# 2. Clear build cache
# 3. Check package.json dependencies
```

**Issue: Authentication not working**
```bash
# Check Cognito User Pool configuration
aws cognito-idp describe-user-pool --user-pool-id YOUR-USER-POOL-ID

# Verify app client settings
aws cognito-idp describe-user-pool-client \
  --user-pool-id YOUR-USER-POOL-ID \
  --client-id YOUR-CLIENT-ID

# Test user creation
aws cognito-idp admin-create-user \
  --user-pool-id YOUR-USER-POOL-ID \
  --username testuser \
  --temporary-password TempPass123!
```

**Issue: API calls failing**
```bash
# Check CORS configuration in API Gateway
# Verify JWT token is being sent correctly
# Check browser developer tools for specific error messages
```

---

## 🔍 Monitoring and Alerting

### Set Up CloudWatch Alarms

```bash
# Lambda error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "Lambda-Errors-XRayExtraction" \
  --alarm-description "Lambda function errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=ab3-xray-XRayExtractionFunction \
  --evaluation-periods 1

# Redshift CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "Redshift-HighCPU" \
  --alarm-description "Redshift high CPU utilization" \
  --metric-name CPUUtilization \
  --namespace AWS/Redshift \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ClusterIdentifier,Value=tco-tbm-ab3 \
  --evaluation-periods 2
```

### Essential Monitoring Queries

```bash
# Check overall system health
aws cloudformation describe-stacks \
  --stack-name ab3-full-stack \
  --query 'Stacks[0].StackStatus'

# Monitor API Gateway 4xx/5xx errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 4XXError \
  --dimensions Name=ApiName,Value=HotelTracingAPI \
  --start-time $(date -d '1 hour ago' -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Sum
```

---

## 🚨 Emergency Procedures

### System-Wide Outage
1. **Check AWS Service Health Dashboard**
2. **Verify CloudFormation stack status**
3. **Review recent deployments or changes**
4. **Check security group configurations**
5. **Validate IAM roles and policies**

### Data Pipeline Failure
1. **Stop all running Glue jobs**
2. **Check S3 data integrity**
3. **Verify Redshift cluster health**
4. **Restart jobs in sequence: Prep → ETL → CRS-RMS**

### Security Incident
1. **Review CloudTrail logs for suspicious activity**
2. **Check WAF blocked requests**
3. **Verify Cognito user activities**
4. **Rotate compromised credentials immediately**

---

## 📞 Support Contacts

- **AWS Support**: Use AWS Support Center for infrastructure issues
- **CloudFormation**: Check stack events for deployment issues
- **Cost Optimization**: Monitor AWS Cost Explorer for unexpected charges
- **Security**: Review AWS Security Hub for security findings

---

## 📚 Additional Resources

- [AWS CloudFormation Troubleshooting](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html)
- [AWS Lambda Troubleshooting](https://docs.aws.amazon.com/lambda/latest/dg/troubleshooting.html)
- [Amazon Redshift Troubleshooting](https://docs.aws.amazon.com/redshift/latest/mgmt/troubleshooting.html)
- [AWS Glue Troubleshooting](https://docs.aws.amazon.com/glue/latest/dg/troubleshooting.html)
- [AWS Amplify Troubleshooting](https://docs.aws.amazon.com/amplify/latest/userguide/troubleshooting.html)