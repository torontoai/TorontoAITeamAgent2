# Backup and Recovery Guide

This document provides detailed instructions for implementing backup and recovery procedures for the TORONTO AI TEAM AGENT system to ensure data safety and business continuity.

## Prerequisites

Before proceeding, ensure you have:
- Completed the [Installation](../getting-started/installation.md) process
- Configured the backend as described in [Backend Configuration](./configuration.md)
- Basic understanding of backup and recovery concepts

## Backup Components

The TORONTO AI TEAM AGENT system requires backup of several key components:

### Database Backup

The primary PostgreSQL database stores:
- User accounts and authentication data
- Project metadata and configuration
- Agent interaction history
- System configuration

### Vector Database Backup

The vector database stores:
- Knowledge embeddings
- Vector indices
- Metadata for knowledge retrieval

### File Storage Backup

File storage contains:
- Training materials
- Generated artifacts
- Uploaded documents
- Temporary files

### Configuration Backup

Configuration files include:
- System configuration
- API keys and credentials
- Environment-specific settings
- Custom configurations

## Backup Strategies

### Regular Database Backup

For PostgreSQL database backup:

```bash
# Manual backup
pg_dump -U toronto_ai -d toronto_ai_team_agent -F c -f /path/to/backups/db_backup_$(date +%Y%m%d).dump

# Automated backup script
cat > /usr/local/bin/backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.dump"

# Create backup
pg_dump -U toronto_ai -d toronto_ai_team_agent -F c -f $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "db_backup_*.dump.gz" -mtime +30 -delete
EOF

# Make script executable
chmod +x /usr/local/bin/backup_database.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_database.sh") | crontab -
```

### Vector Database Backup

For vector database backup:

```bash
# Manual backup using CLI
python -m app.training.cli vector_db --backup --output /path/to/backups/vector_db_backup_$(date +%Y%m%d).zip

# Automated backup script
cat > /usr/local/bin/backup_vector_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vector_db_backup_$TIMESTAMP.zip"

# Create backup
python -m app.training.cli vector_db --backup --output $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "vector_db_backup_*.zip" -mtime +30 -delete
EOF

# Make script executable
chmod +x /usr/local/bin/backup_vector_db.sh

# Add to crontab (daily at 3 AM)
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/backup_vector_db.sh") | crontab -
```

### File Storage Backup

For file storage backup:

```bash
# Manual backup
tar -czf /path/to/backups/files_backup_$(date +%Y%m%d).tar.gz /path/to/toronto_ai_team_agent/data

# Automated backup script
cat > /usr/local/bin/backup_files.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATA_DIR="/path/to/toronto_ai_team_agent/data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz"

# Create backup
tar -czf $BACKUP_FILE $DATA_DIR

# Remove backups older than 30 days
find $BACKUP_DIR -name "files_backup_*.tar.gz" -mtime +30 -delete
EOF

# Make script executable
chmod +x /usr/local/bin/backup_files.sh

# Add to crontab (daily at 4 AM)
(crontab -l 2>/dev/null; echo "0 4 * * * /usr/local/bin/backup_files.sh") | crontab -
```

### Configuration Backup

For configuration backup:

```bash
# Manual backup
tar -czf /path/to/backups/config_backup_$(date +%Y%m%d).tar.gz /path/to/toronto_ai_team_agent/config

# Automated backup script
cat > /usr/local/bin/backup_config.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
CONFIG_DIR="/path/to/toronto_ai_team_agent/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/config_backup_$TIMESTAMP.tar.gz"

# Create backup
tar -czf $BACKUP_FILE $CONFIG_DIR

# Remove backups older than 30 days
find $BACKUP_DIR -name "config_backup_*.tar.gz" -mtime +30 -delete
EOF

# Make script executable
chmod +x /usr/local/bin/backup_config.sh

# Add to crontab (daily at 1 AM)
(crontab -l 2>/dev/null; echo "0 1 * * * /usr/local/bin/backup_config.sh") | crontab -
```

## Comprehensive Backup Solution

For a comprehensive backup solution:

```bash
# Create comprehensive backup script
cat > /usr/local/bin/comprehensive_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATA_DIR="/path/to/toronto_ai_team_agent/data"
CONFIG_DIR="/path/to/toronto_ai_team_agent/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PREFIX="toronto_ai_backup_$TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_PREFIX"

# Database backup
echo "Backing up database..."
pg_dump -U toronto_ai -d toronto_ai_team_agent -F c -f "$BACKUP_DIR/$BACKUP_PREFIX/database.dump"

# Vector database backup
echo "Backing up vector database..."
python -m app.training.cli vector_db --backup --output "$BACKUP_DIR/$BACKUP_PREFIX/vector_db.zip"

# File storage backup
echo "Backing up file storage..."
tar -czf "$BACKUP_DIR/$BACKUP_PREFIX/files.tar.gz" $DATA_DIR

# Configuration backup
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/$BACKUP_PREFIX/config.tar.gz" $CONFIG_DIR

# Create single archive
echo "Creating comprehensive backup archive..."
tar -czf "$BACKUP_DIR/$BACKUP_PREFIX.tar.gz" -C "$BACKUP_DIR" "$BACKUP_PREFIX"

# Clean up
rm -rf "$BACKUP_DIR/$BACKUP_PREFIX"

# Remove backups older than 30 days
find $BACKUP_DIR -name "toronto_ai_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/$BACKUP_PREFIX.tar.gz"
EOF

# Make script executable
chmod +x /usr/local/bin/comprehensive_backup.sh

# Add to crontab (weekly on Sunday at 1 AM)
(crontab -l 2>/dev/null; echo "0 1 * * 0 /usr/local/bin/comprehensive_backup.sh") | crontab -
```

## Offsite Backup

For offsite backup to cloud storage:

### AWS S3

```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Create S3 backup script
cat > /usr/local/bin/s3_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
S3_BUCKET="s3://toronto-ai-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PREFIX="toronto_ai_backup_$TIMESTAMP"

# Run comprehensive backup
/usr/local/bin/comprehensive_backup.sh

# Upload to S3
aws s3 cp "$BACKUP_DIR/$BACKUP_PREFIX.tar.gz" "$S3_BUCKET/"

# Set lifecycle policy on S3 bucket to expire objects after 90 days
EOF

# Make script executable
chmod +x /usr/local/bin/s3_backup.sh

# Add to crontab (weekly on Sunday at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * 0 /usr/local/bin/s3_backup.sh") | crontab -
```

### Google Cloud Storage

```bash
# Install Google Cloud SDK
# Follow instructions at https://cloud.google.com/sdk/docs/install

# Configure Google Cloud credentials
gcloud auth login

# Create GCS backup script
cat > /usr/local/bin/gcs_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
GCS_BUCKET="gs://toronto-ai-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PREFIX="toronto_ai_backup_$TIMESTAMP"

# Run comprehensive backup
/usr/local/bin/comprehensive_backup.sh

# Upload to GCS
gsutil cp "$BACKUP_DIR/$BACKUP_PREFIX.tar.gz" "$GCS_BUCKET/"

# Set lifecycle policy on GCS bucket to expire objects after 90 days
EOF

# Make script executable
chmod +x /usr/local/bin/gcs_backup.sh

# Add to crontab (weekly on Sunday at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * 0 /usr/local/bin/gcs_backup.sh") | crontab -
```

## Recovery Procedures

### Database Recovery

To restore the PostgreSQL database:

```bash
# List available backups
ls -la /path/to/backups/db_backup_*.dump.gz

# Uncompress the backup
gunzip /path/to/backups/db_backup_20250412.dump.gz

# Restore the database
pg_restore -U toronto_ai -d toronto_ai_team_agent -c /path/to/backups/db_backup_20250412.dump
```

### Vector Database Recovery

To restore the vector database:

```bash
# List available backups
ls -la /path/to/backups/vector_db_backup_*.zip

# Restore the vector database
python -m app.training.cli vector_db --restore --input /path/to/backups/vector_db_backup_20250412.zip
```

### File Storage Recovery

To restore file storage:

```bash
# List available backups
ls -la /path/to/backups/files_backup_*.tar.gz

# Restore file storage
tar -xzf /path/to/backups/files_backup_20250412.tar.gz -C /
```

### Configuration Recovery

To restore configuration:

```bash
# List available backups
ls -la /path/to/backups/config_backup_*.tar.gz

# Restore configuration
tar -xzf /path/to/backups/config_backup_20250412.tar.gz -C /
```

### Comprehensive Recovery

To perform a comprehensive recovery:

```bash
# List available comprehensive backups
ls -la /path/to/backups/toronto_ai_backup_*.tar.gz

# Extract the comprehensive backup
tar -xzf /path/to/backups/toronto_ai_backup_20250412_010000.tar.gz -C /path/to/backups/

# Restore database
pg_restore -U toronto_ai -d toronto_ai_team_agent -c /path/to/backups/toronto_ai_backup_20250412_010000/database.dump

# Restore vector database
python -m app.training.cli vector_db --restore --input /path/to/backups/toronto_ai_backup_20250412_010000/vector_db.zip

# Restore file storage
tar -xzf /path/to/backups/toronto_ai_backup_20250412_010000/files.tar.gz -C /

# Restore configuration
tar -xzf /path/to/backups/toronto_ai_backup_20250412_010000/config.tar.gz -C /

# Clean up
rm -rf /path/to/backups/toronto_ai_backup_20250412_010000
```

## Disaster Recovery Plan

### Recovery Time Objectives (RTO)

- **Critical Components**: 4 hours
- **Non-Critical Components**: 24 hours

### Recovery Point Objectives (RPO)

- **Database**: 24 hours (daily backups)
- **Vector Database**: 24 hours (daily backups)
- **File Storage**: 24 hours (daily backups)
- **Configuration**: 24 hours (daily backups)

### Disaster Recovery Procedure

1. **Assessment**:
   - Identify affected components
   - Determine the extent of data loss
   - Select appropriate recovery strategy

2. **Infrastructure Recovery**:
   - Provision new servers if necessary
   - Install required software
   - Configure networking

3. **Data Recovery**:
   - Restore database from latest backup
   - Restore vector database from latest backup
   - Restore file storage from latest backup
   - Restore configuration from latest backup

4. **Verification**:
   - Verify system functionality
   - Verify data integrity
   - Run diagnostic tests

5. **Documentation**:
   - Document the incident
   - Document recovery actions
   - Update recovery procedures if necessary

## Backup Verification

To verify backup integrity:

```bash
# Create backup verification script
cat > /usr/local/bin/verify_backups.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
VERIFY_DIR="/tmp/backup_verification"
LATEST_BACKUP=$(ls -t $BACKUP_DIR/toronto_ai_backup_*.tar.gz | head -1)

# Create verification directory
mkdir -p $VERIFY_DIR
rm -rf $VERIFY_DIR/*

# Extract backup
tar -xzf $LATEST_BACKUP -C $VERIFY_DIR

# Verify database backup
pg_restore --list $VERIFY_DIR/*/database.dump > /dev/null
if [ $? -eq 0 ]; then
  echo "Database backup verification: SUCCESS"
else
  echo "Database backup verification: FAILED"
fi

# Verify vector database backup
python -m app.training.cli vector_db --verify --input $VERIFY_DIR/*/vector_db.zip
if [ $? -eq 0 ]; then
  echo "Vector database backup verification: SUCCESS"
else
  echo "Vector database backup verification: FAILED"
fi

# Verify file storage backup
tar -tzf $VERIFY_DIR/*/files.tar.gz > /dev/null
if [ $? -eq 0 ]; then
  echo "File storage backup verification: SUCCESS"
else
  echo "File storage backup verification: FAILED"
fi

# Verify configuration backup
tar -tzf $VERIFY_DIR/*/config.tar.gz > /dev/null
if [ $? -eq 0 ]; then
  echo "Configuration backup verification: SUCCESS"
else
  echo "Configuration backup verification: FAILED"
fi

# Clean up
rm -rf $VERIFY_DIR
EOF

# Make script executable
chmod +x /usr/local/bin/verify_backups.sh

# Add to crontab (daily at 6 AM)
(crontab -l 2>/dev/null; echo "0 6 * * * /usr/local/bin/verify_backups.sh") | crontab -
```

## Troubleshooting Backup and Recovery Issues

### Common Backup Issues

1. **Insufficient Disk Space**:
   - Monitor disk space usage
   - Implement disk space alerts
   - Configure backup rotation to remove old backups

2. **Backup Process Timeout**:
   - Increase timeout settings
   - Split backups into smaller chunks
   - Schedule backups during low-usage periods

3. **Permission Issues**:
   - Verify backup user permissions
   - Check file and directory permissions
   - Use sudo when necessary

### Common Recovery Issues

1. **Incompatible Backup Format**:
   - Verify backup format compatibility
   - Check software version compatibility
   - Use appropriate recovery tools

2. **Incomplete Recovery**:
   - Verify backup integrity before recovery
   - Follow recovery steps in the correct order
   - Check logs for errors during recovery

3. **Data Corruption**:
   - Maintain multiple backup generations
   - Implement backup verification
   - Test recovery procedures regularly

## Next Steps

- [Backend Configuration](./configuration.md) - For configuring the backend system
- [Backend Monitoring](./monitoring.md) - For monitoring the backend system
- [Scaling Guide](./scaling.md) - For scaling the backend system
