# Canvas LMS Automated Installer for Ubuntu 22.04

A comprehensive, guided installer for Canvas LMS with a beautiful TUI (Text User Interface) that automates the entire installation process on Ubuntu 22.04 LTS servers.

![Canvas LMS Installer](https://img.shields.io/badge/Canvas-LMS-blue) ![Ubuntu 22.04](https://img.shields.io/badge/Ubuntu-22.04-orange) ![Python 3](https://img.shields.io/badge/Python-3.8+-green)

## ⚠️ IMPORTANT: Run the Correct File

**✅ Use this command:**
```bash
sudo python3 install_canvas.py
```

**❌ Do NOT use:**
```bash
sudo python3 canvas_installer.py  # This is the legacy version
```

## ✨ Features

- **Interactive TUI Interface**: Beautiful terminal interface with progress tracking
- **Modular Architecture**: Each installation step is in a separate, editable file
- **Resume Capability**: Installation can be resumed from any failed step
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **Error Handling**: Robust error handling with clear error messages
- **Prerequisites Check**: Automated system requirements verification
- **SSL Support**: Automatic SSL certificate setup with Let's Encrypt
- **Rich Content Editor**: Optional RCE API setup with API key integration
- **Email Configuration**: SMTP setup for Canvas notifications
- **Redis Caching**: Automatic Redis setup and configuration
- **Security Hardening**: Proper file permissions and firewall rules

## 🖥️ System Requirements

- **OS**: Ubuntu 22.04 LTS (Required)
- **RAM**: 8GB minimum
- **CPU**: 4 cores minimum @ 2.0GHz
- **Disk**: 30GB available space
- **Network**: Internet connection required
- **Access**: Root/sudo privileges

## 📋 Prerequisites

Before running the installer, ensure you have:

1. A fresh Ubuntu 22.04 LTS server
2. Root or sudo access
3. A domain name pointing to your server (for SSL)
4. SMTP credentials (optional, for email notifications)
5. API keys for Rich Content Editor (optional):
   - [Flickr API Key](https://www.flickr.com/services/apps/create/apply)
   - [YouTube API Key](https://console.cloud.google.com/)

## 🚀 Quick Start

1. **Download the installer**:
   ```bash
   git clone https://github.com/frazier-at-cpcc/CanvasInstall.git
   cd CanvasInstall
   ```

2. **Make the installer executable**:
   ```bash
   chmod +x install_canvas.py
   ```

3. **Run the installer**:
   ```bash
   sudo python3 install_canvas.py
   ```
   
   The installer will automatically handle dependency installation (Rich library) if not present.

4. **Follow the interactive prompts** to configure your Canvas installation.

### Dependencies Installation

The installer automatically handles the installation of required dependencies (Rich library for the TUI). It will try multiple methods:

1. **Automatic Installation**: Updates packages and installs pip, then installs Rich
2. **Fallback Method**: Uses apt package `python3-rich` if pip fails
3. **Manual Installation**: Provides clear instructions if automatic methods fail

If you encounter dependency issues, you can manually install Rich before running:
```bash
sudo apt update && sudo apt install -y python3-pip && pip3 install rich
# OR
sudo apt install -y python3-rich
```

## 📁 Project Structure

```
CanvasInstall/
├── Article.md                          # Original installation guide
├── README.md                           # This file
├── install_canvas.py                   # Main entry point
├── canvas_installer.py                 # Legacy monolithic installer
└── canvas_installer/                   # Modular installer package
    ├── __init__.py
    ├── config.py                       # Configuration management
    ├── installer.py                    # Main installer class
    ├── utils.py                        # Utility functions
    └── steps/                          # Individual installation steps
        ├── __init__.py
        ├── base_step.py                # Base class for all steps
        ├── step_01_prerequisites.py    # System prerequisites check
        ├── step_02_canvas_user.py      # Create canvas user
        ├── step_03_postgresql.py       # PostgreSQL setup
        ├── step_04_dev_tools.py        # Development tools installation
        ├── step_05_clone_canvas.py     # Canvas LMS cloning
        ├── step_06_configure_canvas.py # Canvas configuration
        ├── step_07_dependencies.py     # Dependencies and assets
        ├── step_08_apache.py           # Apache web server setup
        ├── step_09_ssl.py              # SSL certificate setup
        ├── step_10_virtual_hosts.py    # Apache virtual hosts
        ├── step_11_jobs_firewall.py    # Jobs and firewall setup
        ├── step_12_redis.py            # Redis cache setup
        ├── step_13_rce.py              # Rich Content Editor
        └── step_14_finalize.py         # Final permissions and optimization
```

## ⚙️ Installation Steps

The installer performs the following steps automatically:

1. **Prerequisites Check** - Verifies system requirements
2. **Canvas User Creation** - Creates dedicated canvas user account
3. **PostgreSQL Setup** - Installs and configures PostgreSQL 14
4. **Development Tools** - Installs Git, Ruby 3.3, Node.js 18, Yarn
5. **Canvas Cloning** - Downloads Canvas LMS from official repository
6. **Configuration** - Sets up database, email, and domain configurations
7. **Dependencies** - Installs Ruby gems, Node packages, and compiles assets
8. **Apache Setup** - Installs Apache with Passenger module
9. **SSL Certificate** - Obtains and configures Let's Encrypt SSL (optional)
10. **Virtual Hosts** - Configures Apache virtual hosts for Canvas
11. **Jobs & Firewall** - Sets up automated jobs and firewall rules
12. **Redis Cache** - Installs and configures Redis for caching
13. **Rich Content Editor** - Sets up Canvas RCE API (optional)
14. **Finalization** - Sets permissions and optimizations

## 🔧 Configuration Options

During installation, you'll be prompted for:

- **Domain Name**: Your Canvas domain (e.g., canvas.example.com)
- **Database Password**: PostgreSQL password for canvas user
- **Email Settings**: SMTP server details for notifications
- **API Keys**: Flickr and YouTube API keys for Rich Content Editor
- **SSL Setup**: Whether to configure SSL with Let's Encrypt
- **Optimizations**: Whether to enable file download optimizations

## 📊 Monitoring Installation

The installer provides:

- **Real-time Progress**: Visual progress bars and status updates
- **Detailed Logging**: All operations logged to `canvas_install_YYYYMMDD_HHMMSS.log`
- **Step Tracking**: Clear indication of current installation step
- **Error Messages**: Descriptive error messages with suggestions

## 🔄 Resuming Installation

If installation fails or is interrupted:

1. Run the installer again: `sudo python3 install_canvas.py`
2. Choose "Yes" when prompted to resume from previous state
3. Installation will continue from the last completed step

## 🛠️ Customization

### Modifying Installation Steps

Each step is in a separate file under `canvas_installer/steps/`. To modify a step:

1. Edit the appropriate `step_XX_*.py` file
2. Modify the `execute()` method
3. Follow the base class pattern for consistency

### Adding New Steps

1. Create a new step file: `step_XX_new_feature.py`
2. Inherit from `BaseStep` class
3. Implement required methods: `step_name`, `step_description`, `execute`
4. Add to the steps list in `installer.py`

## 🐛 Troubleshooting

### Common Issues

**Prerequisites Check Failed**
- Ensure you're running Ubuntu 22.04 LTS
- Check that you have sufficient RAM, CPU, and disk space
- Verify internet connectivity

**PostgreSQL Installation Failed**
- Check if PostgreSQL is already installed: `systemctl status postgresql`
- Verify package repositories are accessible

**SSL Certificate Failed**
- Ensure your domain points to the server's IP address
- Check that ports 80 and 443 are accessible
- Verify domain ownership

**Canvas Won't Start**
- Check Apache status: `systemctl status apache2`
- Review Apache error logs: `tail -f /var/log/apache2/error.log`
- Verify Canvas permissions: `ls -la /var/canvas`

### Log Files

- **Installer Log**: `canvas_install_YYYYMMDD_HHMMSS.log`
- **Apache Logs**: `/var/log/apache2/error.log`, `/var/log/apache2/access.log`
- **Canvas Logs**: `/var/canvas/log/production.log`
- **PostgreSQL Logs**: `/var/log/postgresql/postgresql-14-main.log`

### Getting Help

1. Check the installation log file for detailed error messages
2. Ensure all prerequisites are met
3. Try resuming the installation if it was interrupted
4. Review the original article (`Article.md`) for manual steps

## 🔐 Security Considerations

The installer implements several security measures:

- Creates dedicated `canvas` user with limited privileges
- Sets restrictive file permissions on configuration files
- Configures firewall rules with UFW
- Generates secure random keys for Canvas security
- Supports SSL/TLS encryption with Let's Encrypt

## 🚀 Post-Installation

After successful installation:

1. **Access Canvas**: Navigate to `https://your-domain.com`
2. **Complete Setup Wizard**: Follow Canvas's initial setup process
3. **Start RCE Server** (if enabled):
   ```bash
   cd /var/canvas-rce-api
   screen -S canvas-rce-api npm start
   # Press Ctrl+A then D to detach from screen
   ```
4. **Create Admin Account**: Use Canvas web interface to create your first admin user
5. **Configure Institution**: Set up your institution's settings in Canvas

## 📚 Additional Resources

- [Canvas LMS Documentation](https://canvas.instructure.com/doc/)
- [Canvas LMS GitHub Repository](https://github.com/instructure/canvas-lms)
- [Ubuntu 22.04 Documentation](https://help.ubuntu.com/22.04/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and deployment purposes. Canvas LMS is licensed under the AGPLv3 license.

## ⚠️ Disclaimer

This installer is provided without warranty. Always test in a development environment before deploying to production. Ensure you have proper backups and understand the security implications of running a web application.
