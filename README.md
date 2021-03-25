# PwnChain

## Introduction and Goals

PwnChain is a tool for cascading different tools in an automated fashion. Modules with specified input and output domains are linked in a tree structure to fulfill a certain task.

The application is designed for the automatization of penetration testing sequences. Yet the application is aimed to be flexible enough to be used in any scenario where different interdependent CLI tools are processed in order.

PwnChain uses .json configuration files to determine which tools shall be executed in a certain way, using regular expressions to parse the output of a tool to be used as input for subsequent tools. Its goal is to be easily customizable to fulfill different repetitive tasks.