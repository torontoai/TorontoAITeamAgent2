"""
IDE Extensions for TORONTO AI TEAM AGENT.

This module provides functionality to create plugins for VSCode, JetBrains IDEs, etc.,
allowing direct agent assistance within development environments.
"""

import os
import json
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional, Union, Any
from enum import Enum


class IDEType(Enum):
    """Enum representing supported IDE types."""
    VSCODE = "vscode"
    JETBRAINS = "jetbrains"
    ATOM = "atom"
    SUBLIME = "sublime"


class VSCodeExtensionManager:
    """
    Manager class for VSCode extensions.
    
    This class provides functionality to create VSCode extensions that allow
    direct agent assistance within the VSCode development environment.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the VSCode Extension Manager.
        
        Args:
            output_dir: Directory to output generated extensions
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """
        Validate that required dependencies are installed.
        
        Raises:
            RuntimeError: If required dependencies are not installed
        """
        try:
            # Check if Node.js is installed
            subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if npm is installed
            subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if Yeoman and VS Code Extension Generator are installed
            try:
                subprocess.run(
                    ["yo", "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                print("Yeoman is not installed. Installing...")
                subprocess.run(
                    ["npm", "install", "-g", "yo", "generator-code"],
                    capture_output=True,
                    text=True,
                    check=True
                )
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise RuntimeError("Required dependencies (Node.js, npm) are not installed") from e
    
    def create_extension(self, name: str, display_name: str, description: str,
                       publisher: str = "toronto-ai", version: str = "0.0.1",
                       features: List[str] = None) -> str:
        """
        Create a new VSCode extension.
        
        Args:
            name: Extension name (should be kebab-case)
            display_name: Display name for the extension
            description: Extension description
            publisher: Extension publisher
            version: Extension version
            features: List of features to include
            
        Returns:
            Path to the created extension
        """
        if features is None:
            features = ["code-generation", "code-review", "documentation"]
        
        # Create extension directory
        extension_dir = os.path.join(self.output_dir, name)
        os.makedirs(extension_dir, exist_ok=True)
        
        # Create package.json
        package_json = {
            "name": name,
            "displayName": display_name,
            "description": description,
            "version": version,
            "publisher": publisher,
            "engines": {
                "vscode": "^1.60.0"
            },
            "categories": [
                "Other"
            ],
            "activationEvents": [
                "onCommand:extension.torontoAIAssist"
            ],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "extension.torontoAIAssist",
                        "title": "Toronto AI: Get Assistance"
                    }
                ]
            },
            "scripts": {
                "vscode:prepublish": "npm run compile",
                "compile": "tsc -p ./",
                "watch": "tsc -watch -p ./",
                "pretest": "npm run compile && npm run lint",
                "lint": "eslint src --ext ts",
                "test": "node ./out/test/runTest.js"
            },
            "devDependencies": {
                "@types/vscode": "^1.60.0",
                "@types/glob": "^7.1.3",
                "@types/mocha": "^8.2.2",
                "@types/node": "14.x",
                "eslint": "^7.27.0",
                "@typescript-eslint/eslint-plugin": "^4.26.0",
                "@typescript-eslint/parser": "^4.26.0",
                "glob": "^7.1.7",
                "mocha": "^8.4.0",
                "typescript": "^4.3.2",
                "vscode-test": "^1.5.2"
            },
            "dependencies": {
                "axios": "^0.21.1"
            }
        }
        
        # Add feature-specific configurations
        if "code-generation" in features:
            if "contributes" not in package_json:
                package_json["contributes"] = {}
            if "commands" not in package_json["contributes"]:
                package_json["contributes"]["commands"] = []
            
            package_json["contributes"]["commands"].append({
                "command": "extension.generateCode",
                "title": "Toronto AI: Generate Code"
            })
            package_json["activationEvents"].append("onCommand:extension.generateCode")
        
        if "code-review" in features:
            if "contributes" not in package_json:
                package_json["contributes"] = {}
            if "commands" not in package_json["contributes"]:
                package_json["contributes"]["commands"] = []
            
            package_json["contributes"]["commands"].append({
                "command": "extension.reviewCode",
                "title": "Toronto AI: Review Code"
            })
            package_json["activationEvents"].append("onCommand:extension.reviewCode")
        
        if "documentation" in features:
            if "contributes" not in package_json:
                package_json["contributes"] = {}
            if "commands" not in package_json["contributes"]:
                package_json["contributes"]["commands"] = []
            
            package_json["contributes"]["commands"].append({
                "command": "extension.generateDocumentation",
                "title": "Toronto AI: Generate Documentation"
            })
            package_json["activationEvents"].append("onCommand:extension.generateDocumentation")
        
        # Write package.json
        with open(os.path.join(extension_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Create tsconfig.json
        tsconfig_json = {
            "compilerOptions": {
                "module": "commonjs",
                "target": "es6",
                "outDir": "out",
                "lib": [
                    "es6"
                ],
                "sourceMap": True,
                "rootDir": "src",
                "strict": True
            },
            "exclude": [
                "node_modules",
                ".vscode-test"
            ]
        }
        
        # Write tsconfig.json
        with open(os.path.join(extension_dir, "tsconfig.json"), "w") as f:
            json.dump(tsconfig_json, f, indent=2)
        
        # Create src directory
        src_dir = os.path.join(extension_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        # Create extension.ts
        extension_ts = self._generate_extension_ts(features)
        
        # Write extension.ts
        with open(os.path.join(src_dir, "extension.ts"), "w") as f:
            f.write(extension_ts)
        
        # Create README.md
        readme_md = f"""# {display_name}

{description}

## Features

This extension provides the following features:
"""
        
        if "code-generation" in features:
            readme_md += "- **Code Generation**: Generate code based on natural language descriptions\n"
        
        if "code-review" in features:
            readme_md += "- **Code Review**: Get AI-powered code reviews for your code\n"
        
        if "documentation" in features:
            readme_md += "- **Documentation**: Generate documentation for your code\n"
        
        readme_md += """
## Requirements

- Visual Studio Code 1.60.0 or higher

## Extension Settings

This extension contributes the following settings:

* `torontoAI.apiKey`: Your Toronto AI API key

## Known Issues

None at this time.

## Release Notes

### 0.0.1

Initial release of the extension.
"""
        
        # Write README.md
        with open(os.path.join(extension_dir, "README.md"), "w") as f:
            f.write(readme_md)
        
        # Create .vscodeignore
        vscodeignore = """.vscode/**
.vscode-test/**
src/**
.gitignore
.yarnrc
vsc-extension-quickstart.md
**/tsconfig.json
**/.eslintrc.json
**/*.map
**/*.ts
"""
        
        # Write .vscodeignore
        with open(os.path.join(extension_dir, ".vscodeignore"), "w") as f:
            f.write(vscodeignore)
        
        # Initialize npm and install dependencies
        subprocess.run(
            ["npm", "init", "-y"],
            cwd=extension_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        subprocess.run(
            ["npm", "install"],
            cwd=extension_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Compile TypeScript
        subprocess.run(
            ["npm", "run", "compile"],
            cwd=extension_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        return extension_dir
    
    def _generate_extension_ts(self, features: List[str]) -> str:
        """
        Generate the extension.ts file content.
        
        Args:
            features: List of features to include
            
        Returns:
            Content of the extension.ts file
        """
        extension_ts = """import * as vscode from 'vscode';
import * as axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    console.log('Toronto AI Team Agent extension is now active');

    // Register the main assistance command
    let assistDisposable = vscode.commands.registerCommand('extension.torontoAIAssist', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor!');
            return;
        }

        const selection = editor.selection;
        const text = editor.document.getText(selection);

        if (!text) {
            vscode.window.showErrorMessage('No text selected!');
            return;
        }

        try {
            const response = await getAssistance(text);
            showResponse(response);
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    context.subscriptions.push(assistDisposable);
"""
        
        # Add feature-specific commands
        if "code-generation" in features:
            extension_ts += """
    // Register code generation command
    let generateCodeDisposable = vscode.commands.registerCommand('extension.generateCode', async () => {
        const prompt = await vscode.window.showInputBox({
            prompt: 'Describe the code you want to generate',
            placeHolder: 'E.g., A function that sorts an array of objects by a specific property'
        });

        if (!prompt) {
            return;
        }

        try {
            const response = await generateCode(prompt);
            const document = await vscode.workspace.openTextDocument({
                content: response,
                language: detectLanguage(response)
            });
            vscode.window.showTextDocument(document);
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    context.subscriptions.push(generateCodeDisposable);
"""
        
        if "code-review" in features:
            extension_ts += """
    // Register code review command
    let reviewCodeDisposable = vscode.commands.registerCommand('extension.reviewCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor!');
            return;
        }

        const document = editor.document;
        const text = document.getText();

        if (!text) {
            vscode.window.showErrorMessage('No code to review!');
            return;
        }

        try {
            const response = await reviewCode(text);
            showResponse(response);
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    context.subscriptions.push(reviewCodeDisposable);
"""
        
        if "documentation" in features:
            extension_ts += """
    // Register documentation generation command
    let generateDocumentationDisposable = vscode.commands.registerCommand('extension.generateDocumentation', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor!');
            return;
        }

        const document = editor.document;
        const text = document.getText();

        if (!text) {
            vscode.window.showErrorMessage('No code to document!');
            return;
        }

        try {
            const response = await generateDocumentation(text);
            showResponse(response);
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    context.subscriptions.push(generateDocumentationDisposable);
"""
        
        # Add helper functions
        extension_ts += """
}

export function deactivate() {}

async function getAssistance(text: string): Promise<string> {
    // Get API key from settings
    const config = vscode.workspace.getConfiguration('torontoAI');
    const apiKey = config.get<string>('apiKey');

    if (!apiKey) {
        throw new Error('API key not configured. Please set your Toronto AI API key in the extension settings.');
    }

    // Call Toronto AI API
    try {
        const response = await axios.default.post('https://api.torontoai.com/v1/assist', {
            prompt: text,
            max_tokens: 1000
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });

        return response.data.result;
    } catch (error) {
        console.error('API call failed:', error);
        throw new Error('Failed to get assistance from Toronto AI API');
    }
}
"""
        
        if "code-generation" in features:
            extension_ts += """
async function generateCode(prompt: string): Promise<string> {
    // Get API key from settings
    const config = vscode.workspace.getConfiguration('torontoAI');
    const apiKey = config.get<string>('apiKey');

    if (!apiKey) {
        throw new Error('API key not configured. Please set your Toronto AI API key in the extension settings.');
    }

    // Call Toronto AI API
    try {
        const response = await axios.default.post('https://api.torontoai.com/v1/generate-code', {
            prompt: prompt,
            max_tokens: 2000
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });

        return response.data.code;
    } catch (error) {
        console.error('API call failed:', error);
        throw new Error('Failed to generate code using Toronto AI API');
    }
}

function detectLanguage(code: string): string {
    // Simple language detection based on code content
    if (code.includes('function') && code.includes('{') && code.includes('}')) {
        if (code.includes('import React') || code.includes('export default')) {
            return 'javascript';
        }
        if (code.includes('console.log')) {
            return 'javascript';
        }
    }
    
    if (code.includes('def ') && code.includes(':')) {
        return 'python';
    }
    
    if (code.includes('public class') || code.includes('private class')) {
        return 'java';
    }
    
    if (code.includes('#include')) {
        return 'cpp';
    }
    
    return 'plaintext';
}
"""
        
        if "code-review" in features:
            extension_ts += """
async function reviewCode(code: string): Promise<string> {
    // Get API key from settings
    const config = vscode.workspace.getConfiguration('torontoAI');
    const apiKey = config.get<string>('apiKey');

    if (!apiKey) {
        throw new Error('API key not configured. Please set your Toronto AI API key in the extension settings.');
    }

    // Call Toronto AI API
    try {
        const response = await axios.default.post('https://api.torontoai.com/v1/review-code', {
            code: code,
            max_tokens: 2000
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });

        return response.data.review;
    } catch (error) {
        console.error('API call failed:', error);
        throw new Error('Failed to review code using Toronto AI API');
    }
}
"""
        
        if "documentation" in features:
            extension_ts += """
async function generateDocumentation(code: string): Promise<string> {
    // Get API key from settings
    const config = vscode.workspace.getConfiguration('torontoAI');
    const apiKey = config.get<string>('apiKey');

    if (!apiKey) {
        throw new Error('API key not configured. Please set your Toronto AI API key in the extension settings.');
    }

    // Call Toronto AI API
    try {
        const response = await axios.default.post('https://api.torontoai.com/v1/generate-documentation', {
            code: code,
            max_tokens: 2000
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });

        return response.data.documentation;
    } catch (error) {
        console.error('API call failed:', error);
        throw new Error('Failed to generate documentation using Toronto AI API');
    }
}
"""
        
        # Add common helper functions
        extension_ts += """
function showResponse(response: string) {
    // Create and show a new webview panel
    const panel = vscode.window.createWebviewPanel(
        'torontoAIResponse',
        'Toronto AI Response',
        vscode.ViewColumn.Beside,
        {
            enableScripts: true
        }
    );

    // Set the HTML content
    panel.webview.html = getWebviewContent(response);
}

function getWebviewContent(content: string) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toronto AI Response</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
        }
        pre {
            background-color: var(--vscode-editor-background);
            padding: 10px;
            border-radius: 5px;
            overflow: auto;
        }
        code {
            font-family: var(--vscode-editor-font-family);
        }
        .copy-button {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .copy-button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        .container {
            position: relative;
        }
    </style>
</head>
<body>
    <h1>Toronto AI Response</h1>
    <div class="container">
        <button class="copy-button" onclick="copyToClipboard()">Copy</button>
        <pre><code>${escapeHtml(content)}</code></pre>
    </div>
    <script>
        function copyToClipboard() {
            const code = document.querySelector('code').innerText;
            navigator.clipboard.writeText(code).then(() => {
                const button = document.querySelector('.copy-button');
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            });
        }
        
        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
    </script>
</body>
</html>`;
}

function escapeHtml(unsafe: string): string {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
"""
        
        return extension_ts
    
    def package_extension(self, extension_dir: str) -> str:
        """
        Package a VSCode extension as a VSIX file.
        
        Args:
            extension_dir: Path to the extension directory
            
        Returns:
            Path to the packaged VSIX file
        """
        # Check if vsce is installed
        try:
            subprocess.run(
                ["vsce", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            print("vsce is not installed. Installing...")
            subprocess.run(
                ["npm", "install", "-g", "vsce"],
                capture_output=True,
                text=True,
                check=True
            )
        
        # Package the extension
        result = subprocess.run(
            ["vsce", "package"],
            cwd=extension_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract the path to the packaged VSIX file
        for line in result.stdout.splitlines():
            if line.endswith(".vsix"):
                vsix_file = line.strip()
                return os.path.join(extension_dir, vsix_file)
        
        raise RuntimeError("Failed to package extension")


class JetBrainsPluginManager:
    """
    Manager class for JetBrains IDE plugins.
    
    This class provides functionality to create JetBrains IDE plugins that allow
    direct agent assistance within JetBrains development environments.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the JetBrains Plugin Manager.
        
        Args:
            output_dir: Directory to output generated plugins
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """
        Validate that required dependencies are installed.
        
        Raises:
            RuntimeError: If required dependencies are not installed
        """
        try:
            # Check if Java is installed
            subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if Gradle is installed
            try:
                subprocess.run(
                    ["gradle", "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                print("Gradle is not installed. Using Gradle wrapper.")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise RuntimeError("Required dependencies (Java) are not installed") from e
    
    def create_plugin(self, name: str, display_name: str, description: str,
                    vendor: str = "toronto-ai", version: str = "0.0.1",
                    features: List[str] = None) -> str:
        """
        Create a new JetBrains plugin.
        
        Args:
            name: Plugin name (should be camelCase)
            display_name: Display name for the plugin
            description: Plugin description
            vendor: Plugin vendor
            version: Plugin version
            features: List of features to include
            
        Returns:
            Path to the created plugin
        """
        if features is None:
            features = ["code-generation", "code-review", "documentation"]
        
        # Create plugin directory
        plugin_dir = os.path.join(self.output_dir, name)
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create build.gradle
        build_gradle = """plugins {
    id 'org.jetbrains.intellij' version '1.3.0'
    id 'java'
}

group 'com.torontoai'
version '0.0.1'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'com.squareup.okhttp3:okhttp:4.9.1'
    implementation 'com.google.code.gson:gson:2.8.9'
    testImplementation 'org.junit.jupiter:junit-jupiter-api:5.8.1'
    testRuntimeOnly 'org.junit.jupiter:junit-jupiter-engine:5.8.1'
}

// See https://github.com/JetBrains/gradle-intellij-plugin/
intellij {
    version = '2021.2.3'
    type = 'IC' // Target IDE Platform - community edition
    plugins = ['java']
}

test {
    useJUnitPlatform()
}

patchPluginXml {
    changeNotes = \"\"\"
    Initial release of the plugin.
    \"\"\"
}
"""
        
        # Write build.gradle
        with open(os.path.join(plugin_dir, "build.gradle"), "w") as f:
            f.write(build_gradle)
        
        # Create settings.gradle
        settings_gradle = f"rootProject.name = '{name}'"
        
        # Write settings.gradle
        with open(os.path.join(plugin_dir, "settings.gradle"), "w") as f:
            f.write(settings_gradle)
        
        # Create src directory structure
        main_dir = os.path.join(plugin_dir, "src", "main")
        java_dir = os.path.join(main_dir, "java", "com", "torontoai", name)
        resources_dir = os.path.join(main_dir, "resources", "META-INF")
        
        os.makedirs(java_dir, exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)
        
        # Create plugin.xml
        plugin_xml = f"""<idea-plugin>
    <id>com.torontoai.{name}</id>
    <name>{display_name}</name>
    <vendor email="support@torontoai.com" url="https://www.torontoai.com">{vendor}</vendor>

    <description><![CDATA[
    {description}
    ]]></description>

    <!-- please see https://plugins.jetbrains.com/docs/intellij/plugin-compatibility.html
         on how to target different products -->
    <depends>com.intellij.modules.platform</depends>

    <extensions defaultExtensionNs="com.intellij">
        <!-- Add your extensions here -->
    </extensions>

    <actions>
        <group id="TorontoAI.Menu" text="Toronto AI" description="Toronto AI Team Agent">
            <add-to-group group-id="ToolsMenu" anchor="last"/>
            <action id="TorontoAI.GetAssistance" class="com.torontoai.{name}.actions.GetAssistanceAction"
                    text="Get Assistance" description="Get assistance from Toronto AI Team Agent"/>
"""
        
        # Add feature-specific actions
        if "code-generation" in features:
            plugin_xml += f"""            <action id="TorontoAI.GenerateCode" class="com.torontoai.{name}.actions.GenerateCodeAction"
                    text="Generate Code" description="Generate code using Toronto AI Team Agent"/>
"""
        
        if "code-review" in features:
            plugin_xml += f"""            <action id="TorontoAI.ReviewCode" class="com.torontoai.{name}.actions.ReviewCodeAction"
                    text="Review Code" description="Review code using Toronto AI Team Agent"/>
"""
        
        if "documentation" in features:
            plugin_xml += f"""            <action id="TorontoAI.GenerateDocumentation" class="com.torontoai.{name}.actions.GenerateDocumentationAction"
                    text="Generate Documentation" description="Generate documentation using Toronto AI Team Agent"/>
"""
        
        plugin_xml += """        </group>
    </actions>
</idea-plugin>"""
        
        # Write plugin.xml
        with open(os.path.join(resources_dir, "plugin.xml"), "w") as f:
            f.write(plugin_xml)
        
        # Create action classes
        actions_dir = os.path.join(java_dir, "actions")
        os.makedirs(actions_dir, exist_ok=True)
        
        # Create GetAssistanceAction.java
        get_assistance_action = f"""package com.torontoai.{name}.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.CommonDataKeys;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.SelectionModel;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.torontoai.{name}.services.TorontoAIService;
import org.jetbrains.annotations.NotNull;

public class GetAssistanceAction extends AnAction {{

    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {{
        Project project = e.getProject();
        if (project == null) {{
            return;
        }}

        Editor editor = e.getData(CommonDataKeys.EDITOR);
        if (editor == null) {{
            Messages.showErrorDialog("No editor available", "Toronto AI");
            return;
        }}

        SelectionModel selectionModel = editor.getSelectionModel();
        String selectedText = selectionModel.getSelectedText();

        if (selectedText == null || selectedText.isEmpty()) {{
            Messages.showErrorDialog("No text selected", "Toronto AI");
            return;
        }}

        TorontoAIService service = TorontoAIService.getInstance();
        try {{
            String response = service.getAssistance(selectedText);
            service.showResponse(project, "Toronto AI Assistance", response);
        }} catch (Exception ex) {{
            Messages.showErrorDialog("Error: " + ex.getMessage(), "Toronto AI");
        }}
    }}

    @Override
    public void update(@NotNull AnActionEvent e) {{
        // Enable/disable based on whether there's a project open and text selected
        Project project = e.getProject();
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        
        e.getPresentation().setEnabledAndVisible(
            project != null && 
            editor != null && 
            editor.getSelectionModel().hasSelection()
        );
    }}
}}
"""
        
        # Write GetAssistanceAction.java
        with open(os.path.join(actions_dir, "GetAssistanceAction.java"), "w") as f:
            f.write(get_assistance_action)
        
        # Create feature-specific action classes
        if "code-generation" in features:
            generate_code_action = f"""package com.torontoai.{name}.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.torontoai.{name}.services.TorontoAIService;
import org.jetbrains.annotations.NotNull;

public class GenerateCodeAction extends AnAction {{

    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {{
        Project project = e.getProject();
        if (project == null) {{
            return;
        }}

        String prompt = Messages.showInputDialog(
            project,
            "Describe the code you want to generate",
            "Toronto AI Code Generation",
            null
        );

        if (prompt == null || prompt.isEmpty()) {{
            return;
        }}

        TorontoAIService service = TorontoAIService.getInstance();
        try {{
            String response = service.generateCode(prompt);
            service.showResponse(project, "Generated Code", response);
        }} catch (Exception ex) {{
            Messages.showErrorDialog("Error: " + ex.getMessage(), "Toronto AI");
        }}
    }}

    @Override
    public void update(@NotNull AnActionEvent e) {{
        // Enable/disable based on whether there's a project open
        Project project = e.getProject();
        e.getPresentation().setEnabledAndVisible(project != null);
    }}
}}
"""
            
            # Write GenerateCodeAction.java
            with open(os.path.join(actions_dir, "GenerateCodeAction.java"), "w") as f:
                f.write(generate_code_action)
        
        if "code-review" in features:
            review_code_action = f"""package com.torontoai.{name}.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.CommonDataKeys;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.Document;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.torontoai.{name}.services.TorontoAIService;
import org.jetbrains.annotations.NotNull;

public class ReviewCodeAction extends AnAction {{

    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {{
        Project project = e.getProject();
        if (project == null) {{
            return;
        }}

        Editor editor = e.getData(CommonDataKeys.EDITOR);
        if (editor == null) {{
            Messages.showErrorDialog("No editor available", "Toronto AI");
            return;
        }}

        Document document = editor.getDocument();
        String text = document.getText();

        if (text.isEmpty()) {{
            Messages.showErrorDialog("No code to review", "Toronto AI");
            return;
        }}

        TorontoAIService service = TorontoAIService.getInstance();
        try {{
            String response = service.reviewCode(text);
            service.showResponse(project, "Code Review", response);
        }} catch (Exception ex) {{
            Messages.showErrorDialog("Error: " + ex.getMessage(), "Toronto AI");
        }}
    }}

    @Override
    public void update(@NotNull AnActionEvent e) {{
        // Enable/disable based on whether there's a project open and an editor available
        Project project = e.getProject();
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        
        e.getPresentation().setEnabledAndVisible(project != null && editor != null);
    }}
}}
"""
            
            # Write ReviewCodeAction.java
            with open(os.path.join(actions_dir, "ReviewCodeAction.java"), "w") as f:
                f.write(review_code_action)
        
        if "documentation" in features:
            generate_documentation_action = f"""package com.torontoai.{name}.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.CommonDataKeys;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.Document;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.torontoai.{name}.services.TorontoAIService;
import org.jetbrains.annotations.NotNull;

public class GenerateDocumentationAction extends AnAction {{

    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {{
        Project project = e.getProject();
        if (project == null) {{
            return;
        }}

        Editor editor = e.getData(CommonDataKeys.EDITOR);
        if (editor == null) {{
            Messages.showErrorDialog("No editor available", "Toronto AI");
            return;
        }}

        Document document = editor.getDocument();
        String text = document.getText();

        if (text.isEmpty()) {{
            Messages.showErrorDialog("No code to document", "Toronto AI");
            return;
        }}

        TorontoAIService service = TorontoAIService.getInstance();
        try {{
            String response = service.generateDocumentation(text);
            service.showResponse(project, "Generated Documentation", response);
        }} catch (Exception ex) {{
            Messages.showErrorDialog("Error: " + ex.getMessage(), "Toronto AI");
        }}
    }}

    @Override
    public void update(@NotNull AnActionEvent e) {{
        // Enable/disable based on whether there's a project open and an editor available
        Project project = e.getProject();
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        
        e.getPresentation().setEnabledAndVisible(project != null && editor != null);
    }}
}}
"""
            
            # Write GenerateDocumentationAction.java
            with open(os.path.join(actions_dir, "GenerateDocumentationAction.java"), "w") as f:
                f.write(generate_documentation_action)
        
        # Create services directory
        services_dir = os.path.join(java_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        # Create TorontoAIService.java
        toronto_ai_service = f"""package com.torontoai.{name}.services;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import okhttp3.*;
import org.jetbrains.annotations.NotNull;

import javax.swing.*;
import java.awt.*;
import java.io.IOException;

public class TorontoAIService {{
    private static final String API_URL = "https://api.torontoai.com/v1";
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    private static final Gson gson = new Gson();
    private static TorontoAIService instance;
    private final OkHttpClient client = new OkHttpClient();

    private TorontoAIService() {{
        // Private constructor for singleton
    }}

    public static TorontoAIService getInstance() {{
        if (instance == null) {{
            instance = new TorontoAIService();
        }}
        return instance;
    }}

    public String getAssistance(String text) throws IOException {{
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("prompt", text);
        requestBody.addProperty("max_tokens", 1000);

        return makeApiCall(API_URL + "/assist", requestBody.toString(), "result");
    }}

    public String generateCode(String prompt) throws IOException {{
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("prompt", prompt);
        requestBody.addProperty("max_tokens", 2000);

        return makeApiCall(API_URL + "/generate-code", requestBody.toString(), "code");
    }}

    public String reviewCode(String code) throws IOException {{
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("code", code);
        requestBody.addProperty("max_tokens", 2000);

        return makeApiCall(API_URL + "/review-code", requestBody.toString(), "review");
    }}

    public String generateDocumentation(String code) throws IOException {{
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("code", code);
        requestBody.addProperty("max_tokens", 2000);

        return makeApiCall(API_URL + "/generate-documentation", requestBody.toString(), "documentation");
    }}

    private String makeApiCall(String url, String requestBody, String responseField) throws IOException {{
        // In a real implementation, get API key from settings
        String apiKey = "your-api-key";

        RequestBody body = RequestBody.create(requestBody, JSON);
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .addHeader("Authorization", "Bearer " + apiKey)
                .addHeader("Content-Type", "application/json")
                .build();

        try (Response response = client.newCall(request).execute()) {{
            if (!response.isSuccessful()) {{
                throw new IOException("Unexpected response code: " + response);
            }}

            String responseString = response.body().string();
            JsonObject jsonResponse = gson.fromJson(responseString, JsonObject.class);
            
            if (jsonResponse.has(responseField)) {{
                return jsonResponse.get(responseField).getAsString();
            }} else {{
                throw new IOException("Response field not found: " + responseField);
            }}
        }}
    }}

    public void showResponse(Project project, String title, String content) {{
        SwingUtilities.invokeLater(() -> {{
            JTextArea textArea = new JTextArea(content);
            textArea.setEditable(false);
            textArea.setLineWrap(true);
            textArea.setWrapStyleWord(true);
            
            JScrollPane scrollPane = new JScrollPane(textArea);
            scrollPane.setPreferredSize(new Dimension(800, 600));
            
            Messages.showMessageDialog(
                project,
                scrollPane,
                title,
                Messages.getInformationIcon()
            );
        }});
    }}
}}
"""
        
        # Write TorontoAIService.java
        with open(os.path.join(services_dir, "TorontoAIService.java"), "w") as f:
            f.write(toronto_ai_service)
        
        # Create README.md
        readme_md = f"""# {display_name}

{description}

## Features

This plugin provides the following features:
"""
        
        if "code-generation" in features:
            readme_md += "- **Code Generation**: Generate code based on natural language descriptions\n"
        
        if "code-review" in features:
            readme_md += "- **Code Review**: Get AI-powered code reviews for your code\n"
        
        if "documentation" in features:
            readme_md += "- **Documentation**: Generate documentation for your code\n"
        
        readme_md += """
## Requirements

- IntelliJ IDEA 2021.2.3 or higher (or other JetBrains IDEs)

## Installation

1. Download the plugin JAR file
2. In your JetBrains IDE, go to Settings/Preferences > Plugins
3. Click the gear icon and select "Install Plugin from Disk..."
4. Select the downloaded JAR file
5. Restart the IDE when prompted

## Usage

1. Open a project in your JetBrains IDE
2. Go to Tools > Toronto AI to access the plugin features
"""
        
        # Write README.md
        with open(os.path.join(plugin_dir, "README.md"), "w") as f:
            f.write(readme_md)
        
        # Create Gradle wrapper
        subprocess.run(
            ["gradle", "wrapper"],
            cwd=plugin_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        return plugin_dir
    
    def build_plugin(self, plugin_dir: str) -> str:
        """
        Build a JetBrains plugin.
        
        Args:
            plugin_dir: Path to the plugin directory
            
        Returns:
            Path to the built plugin JAR file
        """
        # Build the plugin
        if os.path.exists(os.path.join(plugin_dir, "gradlew")):
            # Use Gradle wrapper
            subprocess.run(
                ["./gradlew", "buildPlugin"],
                cwd=plugin_dir,
                capture_output=True,
                text=True,
                check=True
            )
        else:
            # Use system Gradle
            subprocess.run(
                ["gradle", "buildPlugin"],
                cwd=plugin_dir,
                capture_output=True,
                text=True,
                check=True
            )
        
        # Find the built plugin JAR file
        build_dir = os.path.join(plugin_dir, "build", "libs")
        jar_files = [f for f in os.listdir(build_dir) if f.endswith(".jar")]
        
        if not jar_files:
            raise RuntimeError("No JAR files found in build directory")
        
        return os.path.join(build_dir, jar_files[0])


class IDEExtensionManager:
    """
    Manager class for IDE extensions.
    
    This class provides a unified interface for creating extensions for different IDEs.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the IDE Extension Manager.
        
        Args:
            output_dir: Directory to output generated extensions
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize specific managers
        self.vscode_manager = VSCodeExtensionManager(os.path.join(output_dir, "vscode"))
        self.jetbrains_manager = JetBrainsPluginManager(os.path.join(output_dir, "jetbrains"))
    
    def create_extension(self, ide_type: IDEType, name: str, display_name: str, description: str,
                       publisher: str = "toronto-ai", version: str = "0.0.1",
                       features: List[str] = None) -> str:
        """
        Create a new IDE extension.
        
        Args:
            ide_type: Type of IDE
            name: Extension name
            display_name: Display name for the extension
            description: Extension description
            publisher: Extension publisher
            version: Extension version
            features: List of features to include
            
        Returns:
            Path to the created extension
        """
        if features is None:
            features = ["code-generation", "code-review", "documentation"]
        
        if ide_type == IDEType.VSCODE:
            return self.vscode_manager.create_extension(
                name=name,
                display_name=display_name,
                description=description,
                publisher=publisher,
                version=version,
                features=features
            )
        elif ide_type == IDEType.JETBRAINS:
            return self.jetbrains_manager.create_plugin(
                name=name,
                display_name=display_name,
                description=description,
                vendor=publisher,
                version=version,
                features=features
            )
        else:
            raise ValueError(f"Unsupported IDE type: {ide_type}")
    
    def build_extension(self, ide_type: IDEType, extension_dir: str) -> str:
        """
        Build an IDE extension.
        
        Args:
            ide_type: Type of IDE
            extension_dir: Path to the extension directory
            
        Returns:
            Path to the built extension
        """
        if ide_type == IDEType.VSCODE:
            return self.vscode_manager.package_extension(extension_dir)
        elif ide_type == IDEType.JETBRAINS:
            return self.jetbrains_manager.build_plugin(extension_dir)
        else:
            raise ValueError(f"Unsupported IDE type: {ide_type}")
    
    def create_and_build_extension(self, ide_type: IDEType, name: str, display_name: str,
                                 description: str, publisher: str = "toronto-ai",
                                 version: str = "0.0.1", features: List[str] = None) -> str:
        """
        Create and build a new IDE extension.
        
        Args:
            ide_type: Type of IDE
            name: Extension name
            display_name: Display name for the extension
            description: Extension description
            publisher: Extension publisher
            version: Extension version
            features: List of features to include
            
        Returns:
            Path to the built extension
        """
        extension_dir = self.create_extension(
            ide_type=ide_type,
            name=name,
            display_name=display_name,
            description=description,
            publisher=publisher,
            version=version,
            features=features
        )
        
        return self.build_extension(ide_type, extension_dir)
