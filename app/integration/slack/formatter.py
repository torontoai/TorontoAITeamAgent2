"""
Message formatter for Slack integration.

This module formats messages for Slack.
"""

from typing import Dict, Any, List, Optional, Union
import re
from .models import (
    SlackAttachment, SlackBlock, SlackTextBlock, SlackDividerBlock,
    SlackImageBlock, SlackButtonElement, SlackActionsBlock
)

class SlackFormatter:
    """Formatter for Slack messages."""
    
    @staticmethod
    def text_to_mrkdwn(text: str) -> str:
        """Convert text to Slack's mrkdwn format.
        
        Args:
            text: Text to convert
            
        Returns:
            Converted text
        """
        # Replace HTML-style formatting with Slack mrkdwn
        text = re.sub(r'<b>(.*?)</b>', r'*\1*', text)
        text = re.sub(r'<strong>(.*?)</strong>', r'*\1*', text)
        text = re.sub(r'<i>(.*?)</i>', r'_\1_', text)
        text = re.sub(r'<em>(.*?)</em>', r'_\1_', text)
        text = re.sub(r'<code>(.*?)</code>', r'`\1`', text)
        text = re.sub(r'<pre>(.*?)</pre>', r'```\1```', text)
        
        # Replace Markdown-style links with Slack-style links
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<\2|\1>', text)
        
        return text
    
    @staticmethod
    def create_text_block(text: str) -> SlackTextBlock:
        """Create a text block.
        
        Args:
            text: Block text
            
        Returns:
            Text block
        """
        return SlackTextBlock(text)
    
    @staticmethod
    def create_divider_block() -> SlackDividerBlock:
        """Create a divider block.
        
        Returns:
            Divider block
        """
        return SlackDividerBlock()
    
    @staticmethod
    def create_image_block(
        image_url: str,
        alt_text: str,
        title: Optional[str] = None
    ) -> SlackImageBlock:
        """Create an image block.
        
        Args:
            image_url: Image URL
            alt_text: Alternative text
            title: Optional title
            
        Returns:
            Image block
        """
        return SlackImageBlock(image_url, alt_text, title)
    
    @staticmethod
    def create_button(
        text: str,
        action_id: str,
        value: str,
        style: str = "primary"
    ) -> SlackButtonElement:
        """Create a button element.
        
        Args:
            text: Button text
            action_id: Action identifier
            value: Button value
            style: Button style (primary, danger, or default)
            
        Returns:
            Button element
        """
        return SlackButtonElement(text, action_id, value, style)
    
    @staticmethod
    def create_actions_block(
        elements: List[Union[SlackButtonElement]]
    ) -> SlackActionsBlock:
        """Create an actions block.
        
        Args:
            elements: Block elements
            
        Returns:
            Actions block
        """
        return SlackActionsBlock(elements)
    
    @staticmethod
    def create_attachment(
        fallback: str,
        text: Optional[str] = None,
        title: Optional[str] = None,
        color: Optional[str] = None,
        fields: Optional[List[Dict[str, str]]] = None
    ) -> SlackAttachment:
        """Create an attachment.
        
        Args:
            fallback: Fallback text
            text: Attachment text
            title: Attachment title
            color: Attachment color
            fields: Attachment fields
            
        Returns:
            Attachment
        """
        return SlackAttachment(
            fallback=fallback,
            text=text,
            title=title,
            color=color,
            fields=fields or []
        )
    
    @staticmethod
    def format_code_block(code: str, language: Optional[str] = None) -> str:
        """Format code as a code block.
        
        Args:
            code: Code to format
            language: Programming language
            
        Returns:
            Formatted code block
        """
        if language:
            return f"```{language}\n{code}\n```"
        else:
            return f"```\n{code}\n```"
    
    @staticmethod
    def format_quote(text: str) -> str:
        """Format text as a quote.
        
        Args:
            text: Text to format
            
        Returns:
            Formatted quote
        """
        # Add > to each line
        lines = text.split("\n")
        quoted_lines = [f">{line}" for line in lines]
        return "\n".join(quoted_lines)
    
    @staticmethod
    def format_list(items: List[str], ordered: bool = False) -> str:
        """Format a list.
        
        Args:
            items: List items
            ordered: Whether the list is ordered
            
        Returns:
            Formatted list
        """
        if ordered:
            return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
        else:
            return "\n".join([f"• {item}" for item in items])
    
    @staticmethod
    def format_table(
        headers: List[str],
        rows: List[List[str]]
    ) -> str:
        """Format a table.
        
        Args:
            headers: Table headers
            rows: Table rows
            
        Returns:
            Formatted table as a code block
        """
        # Determine column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell))
        
        # Format headers
        header_row = "| " + " | ".join([h.ljust(w) for h, w in zip(headers, col_widths)]) + " |"
        separator = "| " + " | ".join(["-" * w for w in col_widths]) + " |"
        
        # Format rows
        formatted_rows = []
        for row in rows:
            padded_row = row + [""] * (len(headers) - len(row))  # Pad row if needed
            formatted_row = "| " + " | ".join([cell.ljust(w) for cell, w in zip(padded_row, col_widths)]) + " |"
            formatted_rows.append(formatted_row)
        
        # Combine all parts
        table = "\n".join([header_row, separator] + formatted_rows)
        
        # Return as a code block for proper formatting
        return f"```\n{table}\n```"
