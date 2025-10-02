# 🗄️ Database Backup Utility

A work-in-progress **Database Backup Utility** for safe and reliable database backups.  
Currently, the tool is **early-stage** and requires configuration through command-line arguments.  

---

## 📌 Current Status

✅ Implemented:  
- Backup from **PostgreSQL**  
- Store backups in **Google Cloud Storage (GCS)**  
- CLI-based config (manual flags, no config file yet)  

⚠️ Limitations:  
- No YAML config support yet (all options must be passed through CLI).  
- Limited to PostgreSQL only.  
- No encryption, scheduling, or restore commands implemented yet.  

---

## 🚀 Roadmap

Here’s the development path I’m working on.  
Features are being added incrementally — expect breaking changes until a stable release.

- [x] Backup from PostgreSQL → GCS (MVP complete 🎉)  
- [x] Add support for local storage (MVP complete 🎉)  
- [ ] Launch to PyPI  
- [ ] Add support for AWS S3  
- [ ] Add support for Azure Blob Storage  
- [ ] Add support for MySQL  
- [ ] Add support for MongoDB  
- [ ] Add support for SQLite  
- [ ] Add YAML config file support (to avoid long CLI commands)  
- [ ] Implement restore functionality  
- [ ] Add compression & checksums  
- [ ] Add encryption (GPG or AES)  
- [ ] Add scheduling (cron / built-in job runner)  
- [ ] Add monitoring & notifications (Slack/Email)  

---

## 🛠️ Usage (Current)

Right now, everything runs from CLI flags. Example:

```bash
python backup/cli.py \
  --db-type postgres \
  --db-host localhost \
  --db-port 5432 \
  --db-user admin \
  --db-pass secret \
  --db-name mydb \
  --storage gcs \
  --bucket my-db-backups \
  --project my-gcp-project
```

---

## 🤝 Contribution Policy

At this stage, this project is **not open for public contributions**.  
I am still actively developing the core features, and the roadmap may change quickly.  

If you’re genuinely interested in contributing:  
- Please reach out directly before submitting any pull requests.  
- You can connect with me on [LinkedIn](https://www.linkedin.com/in/asemshaath/) or contact me through another channel.  

Once the project matures, I may open it up for broader community contributions.  

---

## 📅 Vision

The end goal is a **config-driven, multi-DB backup utility** with support for:  
- Multiple databases (Postgres, MySQL, MongoDB, etc.)  
- Multiple storage providers (Local, GCS, AWS S3, Azure Blob)  
- Secure encryption & easy restore  
- Simple automation/scheduling  

---

## 📜 License

MIT License. See `LICENSE` for details.

---

⚡ *This project is still under active development. Expect rough edges, but contributions/feedback are welcome!*  
