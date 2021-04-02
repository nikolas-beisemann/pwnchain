# PwnChain

## Introduction and Goals

PwnChain is a tool for cascading different tools in an automated fashion. Modules with specified input and output domains are linked in a tree structure to fulfill a certain task.

The application is designed for the automatization of penetration testing sequences. Yet the application is aimed to be flexible enough to be used in any scenario where different interdependent CLI tools are processed in order.

PwnChain uses .json configuration files to determine which tools shall be executed in a certain way, using regular expressions to parse the output of a tool to be used as input for subsequent tools. Its goal is to be easily customizable to fulfill different repetitive tasks.

## Warning

PwnChain executes shell commands as instructed by the configuration file. 

**You should never use configuration files that you do not fully understand.**

## Installation

PwnChain requires at least Python 3.8 to run.

### pip (Recommended)

```
python3 -m pip install --upgrade pwnchain
```

### Build Package

```
cd $PWNCHAIN_ROOT
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade dist/pwnchain-*.tar.gz
```

#### Run Tests

```
pytest
```

or

```
cd src
python3 -m pytest ../tests
```

The latter is especially helpful during development.


## Usage

```
python3 -m pwnchain
```

You can use the `-h` or `--help` option to display the various command line options available.

### Example usage

```
python3 -m pwnchain cfg/enumerate.json -sserv:host:10.0.0.1
```

### Configuration

Configuration files are composed in .json format. You can check out the `cfg/` directory of this repository for some usage examples.

The configuration file uses nested module descriptions.

#### Using Variables

In the various configuration strings, variables can be used by `{var_name}`. All variables collected are carried into all subsequent tool executions, defined in the `post` attribute of a module. Redeclaring a variable will override its value for all subsequent tool executions.

Variables can either be declared explicitly using the `vars` attribute, or they can be captured from the tool execution output using the `patterns` attribute.

#### Attributes

Description of a module, identical for the root module, and any modules in the `post` list.

| Attribute   | Description                                                                                            | Example                                |
| ----------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| `name`      | Used for output logging. Mandatory.                                                                    | `"name": "service-discovery"`          |
| `enabled`   | A boolean value indicating whether a module is executed. Defaults to true.                             | `"enabled": false`                     |
| `condition` | Pre-condition which is evaluated to decide whether a module is executed. Can be any python expression. | `"condition": "'{protocol}' == 'ssh'"` |
| `files`     | List of files embedded within the module configuration.                                                | See separate description below         |
| `cmd`       | Command to be executed. Mandatory.                                                                     | `"cmd": "nmap -sV {host}"`             |
| `vars`      | Dictionary of variables directly injected into a module.                                               | `"vars": { "host": "10.0.0.1" }`       |
| `patterns`  | List of pattern dictionaries for capturing variables from module output.                               | See separate description below         |
| `logfile`   | Name of file to use if the `-o` option is used for saving tool output to files.                        | `"logfile": "nmap-{host}.log"`         |
| `submodules`| Dictionary of submodules to be executed after the command has run.                                     | See separate description below         |

The files list shall contain of dictionaries with the following attributes:

| Attribute   | Description                                                                                            | Example                                |
| ----------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| `name`      | Name of the file, which can be used as a variable by the module and its submodules. Mandatory.         | `"name": "wordlist.txt"`               |
| `type`      | One of `text,base64,wget`, for raw text, base64 encoded content, or URI of remote content. Mandatory.  | `"type": "wget"`                       |
| `content`   | Content as specified by `type`. Mandatory.                                                             | `"content": "http://localhost/w.txt"`  |

The patterns list consists of dictionaries with the following attributes:

| Attribute   | Description                                                                                            | Example                                |
| ----------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| `pattern`   | Regular expression using capture groups for variable extraction. Mandatory.                            | `"pattern": "^(\\d+)"`                 |
| `groups`    | List of variable names for the capture groups in order of declaration in the regex. Mandatory.         | `"groups": [ "port" ]`                 |
| `log`       | Message format to output if a pattern was successfully matched.                                        | `"log": "Port {port} identified!"`     |

The submodules dictionary may consist of the following attributes:

| Attribute   | Description                                                                                            | Example                                |
| ----------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| `on_match`  | List of modules to be run when matching a pattern from the `patterns` list.                            | `"on_match": []"`                      |
| `always`    | List of modules to always run after `cmd` has been executed.                                           | `"always": []"`                        |


## License

PwnChain is available under the GPLv3 license. Please see the `LICENSE` file supplied with the software, or at https://www.gnu.org/licenses/