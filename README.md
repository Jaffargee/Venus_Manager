# Venus File Manager

A modern, cross-platform file manager built with Python and PyQt5, featuring a sleek dark theme and comprehensive file management capabilities.

![Venus File Manager](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)

## ✨ Features

### Core File Operations
- **File Navigation**: Intuitive browsing with back/forward navigation history
- **File Operations**: Copy, move, rename, delete files and folders
- **Search**: Real-time file and folder search with filtering
- **Drag & Drop**: Support for dragging files between directories

### Advanced Features
- **Encryption/Decryption**: AES-256 encryption with password protection
- **Compression**: Zip file creation and extraction
- **Trash Management**: Cross-platform trash/recycle bin integration
- **Link Creation**: Create shortcuts and symbolic links
- **Properties**: Detailed file and folder information

### User Interface
- **Dark Theme**: Modern dark UI with customizable styling
- **Responsive Design**: Adaptive layout for different screen sizes
- **Context Menus**: Right-click context menus for quick actions
- **Tabbed Interface**: Multiple directory tabs for efficient workflow
- **Icon View**: Visual file browsing with customizable icon sizes

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python main.py
```

## 📋 Requirements

- **PyQt5**: GUI framework for the desktop application
- **cryptography**: For file encryption/decryption operations

## 🖥️ Usage

### Basic Navigation
1. Launch the application with `python main.py`
2. Use the sidebar to quickly access common directories
3. Double-click folders to navigate
4. Use back/forward buttons for navigation history

### File Operations
- **Copy/Move**: Select files, right-click → Copy/Move
- **Delete**: Right-click → Move to Trash or Delete Permanently
- **Rename**: Select file → F2 or right-click → Rename
- **Create**: Right-click → New Folder

### Advanced Features
- **Search**: Click the search icon and type to filter files
- **Encrypt**: Select files → right-click → Encrypt
- **Compress**: Select files → right-click → Compress
- **Properties**: Right-click → Properties for file details

## 🏗️ Project Structure

```
venus-file-manager/
├── main.py                 # Application entry point
├── containers.py           # Title bar and UI containers
├── file_manager_.py        # Main file manager widget
├── SideBar.py             # Directory sidebar component
├── menu.py                # Context menu definitions
├── filedialog.py          # File selection dialogs
├── gui_download.py        # Download interface
├── linux_diskmanager.py   # Linux disk management
├── disk_managment.py      # Disk management utilities
├── ziping.py             # Compression utilities
├── encrption.py          # Legacy encryption (deprecated)
├── trash_module.py       # Legacy trash (deprecated)
├── venus/                 # UI styling
│   └── venus_st.css      # Dark theme stylesheets
├── icons/                 # Application icons
├── file_operations_api.py # Core file operations API
├── encryption_api.py     # Encryption/decryption API
├── download_api.py       # Download management API
├── trash_api.py          # Cross-platform trash API
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 🔧 API Architecture

The application uses a modular API architecture:

- **file_operations_api.py**: Handles all basic file operations (copy, move, delete, etc.)
- **encryption_api.py**: Manages AES-256 encryption/decryption
- **download_api.py**: Background file downloading
- **trash_api.py**: Cross-platform trash management

## 🎨 Customization

### Themes
The application uses CSS styling located in `venus/venus_st.css`. You can customize:
- Colors and gradients
- Font sizes and families
- Button styles and hover effects
- Layout spacing and margins

### Icons
Icons are stored in the `icons/` directory. Replace or add new icons as needed.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

### Development Setup
```bash
git clone https://github.com/Jaffargee/venus-file-manager.git
cd venus-file-manager
pip install -r requirements.txt
python main.py
```

### Quick Start for Contributors
1. Fork and clone the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## 🔄 CI/CD

This project uses GitHub Actions for continuous integration:

- **Automated Testing**: Runs on multiple Python versions (3.10, 3.11, 3.12)
- **Cross-Platform**: Tests on both Ubuntu and Windows
- **Import Validation**: Ensures all modules can be imported successfully

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyQt5](https://pypi.org/project/PyQt5/)
- Encryption powered by [cryptography](https://cryptography.io/)
- Icons from various open-source collections

## 📞 Contact

For questions, bug reports, or feature requests:
- Create an issue on GitHub
- Email: [your-email@example.com]

---

**Venus File Manager** - A powerful, modern file manager for the desktop.