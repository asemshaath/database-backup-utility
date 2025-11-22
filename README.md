# Afterchive - A Database Backup Orchestrator

A work-in-progress **Database Backup Utility Orchestrator** for safe and reliable database backups.  
Currently, the tool is **early-stage** and requires configuration through command-line arguments.  

---
## Overview

When I was a software engineer at Hughes, I used to write shell scripts that was heavily backing up data. Therefore, I wanted to build this tool that will be helpful with managing databases between machine and cloud storage. The tool is open source to support other engineers.  

![alt text](.media/image.png)

---

## Roadmap

### v0.1.0 (Current) ✅
- [x] PostgreSQL backup/restore
- [x] GCS and Local storage
- [x] YAML configuration
- [x] Environment variable support

### v0.2.0 (Planned)
- [ ] Launch to PyPI  
- [ ] MySQL support
- [ ] AWS S3 storage
- [ ] Compression & checksums
- [ ] Retention policies

### v0.3.0 (Planned)
- [ ] MongoDB support
- [ ] Azure Blob storage
- [ ] Scheduling (cron / built-in job runner)

### v1.0.0 (Planned)
- [ ] Multiple backup jobs
- [ ] Notifications (Slack, Email)
- [ ] Encryption (GPG or AES)
- [ ] Advanced orchestration

---

## Test Requirments

The tool needs to be tested in diffrent environments

- [ ] Test the code for PostgreSQL to GCS in local enviroment
- [ ] Test the running status in multiple linux enviroments

---

## Requirements
#### PostgreSQL Version Requirements

**IMPORTANT:** Your `pg_dump` version must be >= your database version.


---

## Usage (Current)

Right now, everything runs from CLI flags. Example:

> Please note: this is subject to change as this package is not deployed to PyPI

```bash
python core/cli.py backup\
  --db-type postgres \ # this would be to specfiy the db type (e.g. postgres or mysql)
  --db-host localhost \
  --db-port 5432 \
  --db-user admin \
  --db-pass bigsecret \ # when password not provideed user will be prompted
  --db-name collegegrades \
  --storage gcs \
  --bucket my-db-backups \
  --path dbbu\ # the path of the directory (not file name) 
  --project my-gcp-project # project name would mostly be optional
```

---

## Contribution Policy

At this stage, this project is **not open for public contributions**.  
I am still actively developing the core features, and the roadmap may change quickly.  

If you’re genuinely interested in contributing:  
- Please reach out directly before submitting any pull requests.  
- You can connect with me on [LinkedIn](https://www.linkedin.com/in/asemshaath/) or contact me through another channel.  

Once the project matures, I may open it up for broader community contributions.  

---

## Vision

The end goal is a **config-driven, multi-DB backup orchestrator** with support for:  
- Multiple databases (Postgres, MySQL, MongoDB, etc.)  
- Multiple storage providers (Local, GCS, AWS S3, Azure Blob)  
- Secure encryption & easy restore  
- Simple automation/scheduling  

The end goal will have 3 main functionalities:
- 1 db &harr; 1 storage location
- 1 db &harr; multiple storage locations
- multiple databases &harr; multiple storage locations
---

## License

MIT License. See `LICENSE` for details.

---

*This project is still under active development. Expect rough edges, but contributions/feedback are welcome!*  
*This project is inspired by https://roadmap.sh/projects/database-backup-utility*
