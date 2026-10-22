<div align="center">

<!-- Main animated headline -->
<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=30&pause=1000&color=00F3FF&center=true&vCenter=true&width=500&height=50&lines=NYXAEV-Toolbox;Secure+Local+Utilities;Password,+UUID+%26+JSON+Tools" alt="Typing Title" />
</h1>

<p align="center">
  <strong>A secure, lightweight local development utility suite built with Python.</strong>
</p>

<!-- Badges section -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Security-Localhost%20Only-00F3FF?style=for-the-badge&logo=shield&logoColor=black" alt="Security"/>
  <img src="https://img.shields.io/badge/License-MIT-9900FF?style=for-the-badge" alt="License"/>
</p>

---

</div>

## 🌌 Overview

**NYXAEV Toolbox** is a robust, self-contained local utility web application designed for developers. It runs entirely on your machine with strict local security controls, offering lightning-fast tools for everyday development workflows.

---

## 🛠️ Features & Tools

<div align="center">

<table>
  <tr>
    <td width="33%" align="center">
      <h3>🔐 Password Generator</h3>
      <p><em>Cryptographically secure</em></p>
      <ul align="left">
        <li>Powered by Python's <code>secrets</code> module</li>
        <li>Customizable length & char sets</li>
        <li>Filter ambiguous chars (<code>Il1O0o</code>)</li>
        <li>Real-time entropy estimation</li>
      </ul>
    </td>
    <td width="33%" align="center">
      <h3>🆔 UUID Generator</h3>
      <p><em>Unique identifier suite</em></p>
      <ul align="left">
        <li>Supports versions <strong>v4, v1, v3, v5</strong></li>
        <li>Uppercase & hyphen toggles</li>
        <li>One-click copy actions</li>
      </ul>
    </td>
    <td width="33%" align="center">
      <h3>📋 JSON Converter</h3>
      <p><em>Formatter & Validator</em></p>
      <ul align="left">
        <li>Format, minify, or validate</li>
        <li>Custom indentation & sorted keys</li>
        <li>Precise error reporting (line & column)</li>
      </ul>
    </td>
  </tr>
</table>

</div>

---

## 🛡️ Security & Behavior

- **Localhost Only:** Bound exclusively to `127.0.0.1`—nothing is ever exposed to your local network.
- **Strict Validation:** Accepts only local host requests; API endpoints explicitly enforce `application/json`.
- **Port Fallback:** If default port `8765` is busy, it automatically scans and binds to the next available port.

---

## 🚀 Quick Start

### 1. Requirements & Extraction
Extract the provided `nyxaev-toolbox.zip` archive to a folder of your choice. Make sure you have **Python 3.8+** installed.

### 2. Running the Tool
Open your terminal inside the extracted directory and run:

```bash
python toolbox.py
