# **netapp_inodes_toolkit**

This Python script Effortlessly manage inode capacity in your NETAPP storage system, ensuring peak performance while preventing capacity issues.


## **Features**

- **Dynamic Scaling**: Automatically increases inode limits by a default percentage (15%).
- **Target Specific Volumes**: Optionally focus on specific volumes for precise inode control.
- **Built-in Safety Mechanisms**: Prevents excessive inode scaling with user confirmations and strict limits.
- **Detailed Logging**: Logs all actions and errors for audit and troubleshooting purposes.

## **Prerequisites**

- Python 3.6 or higher
- Required Python libraries:
  - `requests`
  - `docopt`

Install dependencies using:
```bash
pip install requests docopt
```

## **Usage**

### **Command-Line Options**

```text
Usage:
  add_inodes.py -s <storage_address> [-v <volume_name>] [-p <percent>]
  add_inodes.py (-h | --help)
  add_inodes.py --version

Options:
  -s <storage_address>    Address of the storage system (required).
  -v <volume_name>        Name of the specific volume to check (optional).
  -p <percent>            Percentage of inodes to add (optional, default: 15%).
  -h --help               Show this help message.
  --version               Show script version.
```

### **Examples**

1. **Scale inodes by default 15% across all volumes:**

```bash
python add_inodes.py -s 192.168.1.1
```

2. **Scale inodes by 20% for a specific volume:**

```bash
python add_inodes.py -s 192.168.1.1 -v my_volume -p 20
```

3. **Display help information:**

```bash
python add_inodes.py --help
```

## **How It Works**

1. **Authentication:**
   - The script uses HTTP Basic Authentication to securely connect to your storage system.

2. **Monitor Inodes:**
   - Fetches inode usage for all or specific volumes.
   - Identifies volumes where inode usage exceeds 90% of the current capacity.

3. **Scale Inodes:**
   - Calculates the new inode limit based on the specified percentage.
   - Updates the storage system using a PATCH API call.

4. **Safety Features:**
   - Prompts for confirmation if scaling exceeds 15% but is under the maximum limit of 25%.
   - Prevents scaling beyond 25% to ensure system stability.

## **Logging**

All script actions and errors are logged in `add_inodes.log`. This includes:
- API responses
- Inode scaling details
- Error messages



## **Contributing**

Contributions are welcome! If you have suggestions for improvements or encounter issues, please open an issue or submit a pull request on GitHub.

## **License**

This project is licensed under the MIT License. See the LICENSE file for details.
