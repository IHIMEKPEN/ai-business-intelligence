"""
Action Executor Agent

Responsible for executing actions and implementing recommendations:
- Action execution
- Report generation
- Notification sending
- Integration with external systems
- Workflow automation
"""

import asyncio
import json
import smtplib
import requests
from typing import Dict, List, Any, Optional, Tuple
import structlog
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

from core.agent_framework import BaseAgent, AgentType, Task, Message
from core.communication import communication_manager

logger = structlog.get_logger(__name__)


class ActionExecutorAgent(BaseAgent):
    """
    Action Executor Agent for implementing recommendations and executing actions
    
    Capabilities:
    - Action execution
    - Report generation
    - Notification sending
    - Integration with external systems
    - Workflow automation
    - Email notifications
    - API integrations
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id or f"action_executor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            agent_type=AgentType.ACTION_EXECUTOR,
            name="Action Executor Agent"
        )
        
        self.capabilities = [
            "action_execution",
            "report_generation",
            "notification_sending",
            "external_integration",
            "workflow_automation",
            "email_notifications",
            "api_integrations"
        ]
        
        self.action_history = []
        self.execution_status = {}
        self.external_apis = {}
        self.notification_templates = {}
        
        # Initialize notification templates
        self._initialize_notification_templates()
        
        logger.info(
            "Action Executor Agent initialized",
            agent_id=self.agent_id,
            capabilities=self.capabilities
        )
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process action execution tasks"""
        task_type = task.name
        parameters = task.parameters
        
        logger.info(
            "Processing action execution task",
            task_id=task.id,
            task_type=task_type,
            parameters=parameters
        )
        
        try:
            if task_type == "execute_action":
                return await self._execute_action(parameters)
            elif task_type == "generate_report":
                return await self._generate_report(parameters)
            elif task_type == "send_notification":
                return await self._send_notification(parameters)
            elif task_type == "api_integration":
                return await self._api_integration(parameters)
            elif task_type == "workflow_automation":
                return await self._workflow_automation(parameters)
            elif task_type == "email_notification":
                return await self._email_notification(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(
                "Task processing failed",
                task_id=task.id,
                task_type=task_type,
                error=str(e)
            )
            raise
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        message_type = message.message_type
        
        if message_type == "action_request":
            return await self._handle_action_request(message)
        elif message_type == "notification_request":
            return await self._handle_notification_request(message)
        elif message_type == "report_request":
            return await self._handle_report_request(message)
        else:
            logger.warning(
                "Unknown message type",
                message_type=message_type,
                agent_id=self.agent_id
            )
            return None
    
    async def _execute_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action"""
        action_type = parameters.get("action_type")
        action_data = parameters.get("action_data", {})
        priority = parameters.get("priority", "medium")
        
        if not action_type:
            raise ValueError("No action type specified")
        
        try:
            action_id = f"action_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Execute action based on type
            if action_type == "data_export":
                result = await self._execute_data_export(action_data)
            elif action_type == "system_configuration":
                result = await self._execute_system_configuration(action_data)
            elif action_type == "workflow_trigger":
                result = await self._execute_workflow_trigger(action_data)
            elif action_type == "external_api_call":
                result = await self._execute_external_api_call(action_data)
            elif action_type == "notification_send":
                result = await self._execute_notification_send(action_data)
            else:
                result = {"status": "unknown_action_type", "error": f"Unknown action type: {action_type}"}
            
            # Record action in history
            action_record = {
                "action_id": action_id,
                "action_type": action_type,
                "parameters": action_data,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": priority
            }
            
            self.action_history.append(action_record)
            self.execution_status[action_id] = result
            
            logger.info(
                "Action executed",
                action_id=action_id,
                action_type=action_type,
                status=result.get("status", "unknown"),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "execute_action",
                "action_id": action_id,
                "action_type": action_type,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Action execution failed",
                action_type=action_type,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _generate_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and format reports"""
        report_type = parameters.get("report_type", "standard")
        report_data = parameters.get("report_data", {})
        format_type = parameters.get("format", "json")
        output_path = parameters.get("output_path")
        
        try:
            report_id = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate report content
            if report_type == "business_intelligence":
                report_content = await self._generate_business_intelligence_report(report_data)
            elif report_type == "performance_analysis":
                report_content = await self._generate_performance_analysis_report(report_data)
            elif report_type == "recommendation_summary":
                report_content = await self._generate_recommendation_summary_report(report_data)
            else:
                report_content = await self._generate_standard_report(report_data)
            
            # Format report
            if format_type == "json":
                formatted_report = json.dumps(report_content, indent=2)
            elif format_type == "html":
                formatted_report = await self._format_report_as_html(report_content)
            elif format_type == "csv":
                formatted_report = await self._format_report_as_csv(report_content)
            else:
                formatted_report = str(report_content)
            
            # Save report if output path specified
            if output_path:
                await self._save_report(formatted_report, output_path, format_type)
            
            logger.info(
                "Report generated",
                report_id=report_id,
                report_type=report_type,
                format=format_type,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "generate_report",
                "report_id": report_id,
                "report_type": report_type,
                "format": format_type,
                "content": formatted_report,
                "output_path": output_path,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Report generation failed",
                report_type=report_type,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _send_notification(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send notifications through various channels"""
        notification_type = parameters.get("notification_type", "email")
        recipients = parameters.get("recipients", [])
        message = parameters.get("message", "")
        subject = parameters.get("subject", "AI Business Intelligence Notification")
        priority = parameters.get("priority", "normal")
        
        if not recipients:
            raise ValueError("No recipients specified for notification")
        
        try:
            notification_id = f"notification_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Send notification based on type
            if notification_type == "email":
                result = await self._send_email_notification(recipients, subject, message, priority)
            elif notification_type == "slack":
                result = await self._send_slack_notification(recipients, message, priority)
            elif notification_type == "webhook":
                result = await self._send_webhook_notification(recipients, message, priority)
            else:
                result = {"status": "unknown_notification_type", "error": f"Unknown notification type: {notification_type}"}
            
            logger.info(
                "Notification sent",
                notification_id=notification_id,
                notification_type=notification_type,
                recipient_count=len(recipients),
                status=result.get("status", "unknown"),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "send_notification",
                "notification_id": notification_id,
                "notification_type": notification_type,
                "recipients": recipients,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Notification sending failed",
                notification_type=notification_type,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _api_integration(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with external APIs"""
        api_name = parameters.get("api_name")
        endpoint = parameters.get("endpoint")
        method = parameters.get("method", "GET")
        data = parameters.get("data", {})
        headers = parameters.get("headers", {})
        
        if not api_name or not endpoint:
            raise ValueError("API name and endpoint are required")
        
        try:
            integration_id = f"integration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Make API call
            result = await self._make_api_call(api_name, endpoint, method, data, headers)
            
            logger.info(
                "API integration completed",
                integration_id=integration_id,
                api_name=api_name,
                endpoint=endpoint,
                status=result.get("status", "unknown"),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "api_integration",
                "integration_id": integration_id,
                "api_name": api_name,
                "endpoint": endpoint,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "API integration failed",
                api_name=api_name,
                endpoint=endpoint,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _workflow_automation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Automate workflows and processes"""
        workflow_name = parameters.get("workflow_name")
        workflow_steps = parameters.get("workflow_steps", [])
        trigger_conditions = parameters.get("trigger_conditions", {})
        
        if not workflow_name:
            raise ValueError("Workflow name is required")
        
        try:
            workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Execute workflow
            result = await self._execute_workflow(workflow_name, workflow_steps, trigger_conditions)
            
            logger.info(
                "Workflow automation completed",
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                steps_executed=len(workflow_steps),
                status=result.get("status", "unknown"),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "workflow_automation",
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Workflow automation failed",
                workflow_name=workflow_name,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _email_notification(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notifications"""
        recipients = parameters.get("recipients", [])
        subject = parameters.get("subject", "AI Business Intelligence Alert")
        message = parameters.get("message", "")
        template_name = parameters.get("template", "default")
        
        if not recipients:
            raise ValueError("No recipients specified for email notification")
        
        try:
            # Get email template
            template = self.notification_templates.get(template_name, self.notification_templates["default"])
            
            # Format message using template
            formatted_message = template.format(
                subject=subject,
                message=message,
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                system_name="AI Business Intelligence System"
            )
            
            # Send email
            result = await self._send_email(recipients, subject, formatted_message)
            
            logger.info(
                "Email notification sent",
                recipients=recipients,
                template=template_name,
                status=result.get("status", "unknown"),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "email_notification",
                "recipients": recipients,
                "template": template_name,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Email notification failed",
                recipients=recipients,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    # Action execution methods
    async def _execute_data_export(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data export action"""
        export_format = action_data.get("format", "csv")
        data = action_data.get("data", [])
        file_path = action_data.get("file_path", f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_format}")
        
        try:
            if export_format == "csv":
                import pandas as pd
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
            elif export_format == "json":
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                return {"status": "error", "message": f"Unsupported export format: {export_format}"}
            
            return {
                "status": "success",
                "file_path": file_path,
                "export_format": export_format,
                "record_count": len(data)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_system_configuration(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system configuration action"""
        config_type = action_data.get("config_type")
        config_data = action_data.get("config_data", {})
        
        try:
            # Simulate configuration update
            if config_type == "agent_settings":
                # Update agent settings
                pass
            elif config_type == "notification_settings":
                # Update notification settings
                pass
            elif config_type == "api_settings":
                # Update API settings
                pass
            
            return {
                "status": "success",
                "config_type": config_type,
                "config_updated": True
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_workflow_trigger(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow trigger action"""
        workflow_name = action_data.get("workflow_name")
        trigger_data = action_data.get("trigger_data", {})
        
        try:
            # Simulate workflow trigger
            return {
                "status": "success",
                "workflow_name": workflow_name,
                "triggered": True,
                "trigger_data": trigger_data
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_external_api_call(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute external API call action"""
        api_url = action_data.get("api_url")
        method = action_data.get("method", "GET")
        headers = action_data.get("headers", {})
        data = action_data.get("data", {})
        
        try:
            response = requests.request(
                method=method,
                url=api_url,
                headers=headers,
                json=data if method in ["POST", "PUT", "PATCH"] else None,
                params=data if method == "GET" else None,
                timeout=30
            )
            
            return {
                "status": "success",
                "response_status": response.status_code,
                "response_data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_notification_send(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification send action"""
        notification_type = action_data.get("notification_type", "email")
        recipients = action_data.get("recipients", [])
        message = action_data.get("message", "")
        
        try:
            if notification_type == "email":
                result = await self._send_email_notification(recipients, "Notification", message)
            else:
                result = {"status": "unknown_type", "message": f"Unknown notification type: {notification_type}"}
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # Report generation methods
    async def _generate_business_intelligence_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business intelligence report"""
        return {
            "report_type": "business_intelligence",
            "generated_at": datetime.utcnow().isoformat(),
            "executive_summary": report_data.get("executive_summary", ""),
            "key_insights": report_data.get("key_insights", []),
            "recommendations": report_data.get("recommendations", []),
            "metrics": report_data.get("metrics", {}),
            "trends": report_data.get("trends", {}),
            "risk_assessment": report_data.get("risk_assessment", {}),
            "next_steps": report_data.get("next_steps", [])
        }
    
    async def _generate_performance_analysis_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance analysis report"""
        return {
            "report_type": "performance_analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "performance_metrics": report_data.get("performance_metrics", {}),
            "kpi_analysis": report_data.get("kpi_analysis", {}),
            "trend_analysis": report_data.get("trend_analysis", {}),
            "benchmarking": report_data.get("benchmarking", {}),
            "improvement_areas": report_data.get("improvement_areas", []),
            "action_items": report_data.get("action_items", [])
        }
    
    async def _generate_recommendation_summary_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation summary report"""
        return {
            "report_type": "recommendation_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "recommendations": report_data.get("recommendations", []),
            "prioritization": report_data.get("prioritization", {}),
            "implementation_plan": report_data.get("implementation_plan", {}),
            "expected_impact": report_data.get("expected_impact", {}),
            "resource_requirements": report_data.get("resource_requirements", {}),
            "timeline": report_data.get("timeline", {})
        }
    
    async def _generate_standard_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate standard report"""
        return {
            "report_type": "standard",
            "generated_at": datetime.utcnow().isoformat(),
            "content": report_data.get("content", {}),
            "metadata": report_data.get("metadata", {})
        }
    
    async def _format_report_as_html(self, report_content: Dict[str, Any]) -> str:
        """Format report as HTML"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Business Intelligence Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .section { margin: 20px 0; }
                .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }
                .recommendation { background-color: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>AI Business Intelligence Report</h1>
                <p>Generated: {timestamp}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p>{executive_summary}</p>
            </div>
            
            <div class="section">
                <h2>Key Insights</h2>
                {insights_html}
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {recommendations_html}
            </div>
        </body>
        </html>
        """
        
        # Extract data for HTML formatting
        executive_summary = report_content.get("executive_summary", "No executive summary available.")
        insights = report_content.get("key_insights", [])
        recommendations = report_content.get("recommendations", [])
        
        # Format insights
        insights_html = ""
        for insight in insights:
            if isinstance(insight, dict):
                insights_html += f'<div class="metric"><strong>{insight.get("title", "Insight")}</strong><br>{insight.get("description", "")}</div>'
            else:
                insights_html += f'<div class="metric">{insight}</div>'
        
        # Format recommendations
        recommendations_html = ""
        for rec in recommendations:
            if isinstance(rec, dict):
                recommendations_html += f'<div class="recommendation"><strong>{rec.get("title", "Recommendation")}</strong><br>{rec.get("description", "")}</div>'
            else:
                recommendations_html += f'<div class="recommendation">{rec}</div>'
        
        return html_template.format(
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            executive_summary=executive_summary,
            insights_html=insights_html,
            recommendations_html=recommendations_html
        )
    
    async def _format_report_as_csv(self, report_content: Dict[str, Any]) -> str:
        """Format report as CSV"""
        import pandas as pd
        
        # Convert report content to CSV format
        csv_data = []
        
        # Add metadata
        csv_data.append(["Report Type", report_content.get("report_type", "unknown")])
        csv_data.append(["Generated At", report_content.get("generated_at", "")])
        csv_data.append([])
        
        # Add insights
        csv_data.append(["Key Insights"])
        insights = report_content.get("key_insights", [])
        for insight in insights:
            if isinstance(insight, dict):
                csv_data.append([insight.get("title", ""), insight.get("description", "")])
            else:
                csv_data.append([insight])
        
        csv_data.append([])
        
        # Add recommendations
        csv_data.append(["Recommendations"])
        recommendations = report_content.get("recommendations", [])
        for rec in recommendations:
            if isinstance(rec, dict):
                csv_data.append([rec.get("title", ""), rec.get("description", "")])
            else:
                csv_data.append([rec])
        
        # Convert to CSV string
        df = pd.DataFrame(csv_data)
        return df.to_csv(index=False, header=False)
    
    async def _save_report(self, report_content: str, output_path: str, format_type: str):
        """Save report to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(
                "Report saved",
                output_path=output_path,
                format=format_type,
                agent_id=self.agent_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to save report",
                output_path=output_path,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    # Notification methods
    async def _send_email_notification(self, recipients: List[str], subject: str, message: str, priority: str = "normal") -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Check if email configuration is available
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            
            if not all([smtp_server, smtp_username, smtp_password]):
                return {
                    "status": "error",
                    "message": "Email configuration not available"
                }
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            return {
                "status": "success",
                "recipients": recipients,
                "subject": subject
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _send_slack_notification(self, recipients: List[str], message: str, priority: str = "normal") -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            
            if not webhook_url:
                return {
                    "status": "error",
                    "message": "Slack webhook URL not configured"
                }
            
            # Prepare Slack message
            slack_data = {
                "text": message,
                "channel": recipients[0] if recipients else "#general"
            }
            
            # Send to Slack
            response = requests.post(webhook_url, json=slack_data, timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "recipients": recipients,
                    "slack_response": "Message sent successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Slack API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _send_webhook_notification(self, recipients: List[str], message: str, priority: str = "normal") -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            webhook_url = recipients[0] if recipients else None
            
            if not webhook_url:
                return {
                    "status": "error",
                    "message": "No webhook URL provided"
                }
            
            # Prepare webhook data
            webhook_data = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": priority,
                "source": "ai_business_intelligence"
            }
            
            # Send webhook
            response = requests.post(webhook_url, json=webhook_data, timeout=10)
            
            return {
                "status": "success" if response.status_code < 400 else "error",
                "webhook_url": webhook_url,
                "response_status": response.status_code,
                "response_text": response.text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _send_email(self, recipients: List[str], subject: str, message: str) -> Dict[str, Any]:
        """Send email using configured SMTP"""
        return await self._send_email_notification(recipients, subject, message)
    
    # API integration methods
    async def _make_api_call(self, api_name: str, endpoint: str, method: str, data: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to external service"""
        try:
            # Add API-specific headers if needed
            if api_name in self.external_apis:
                api_config = self.external_apis[api_name]
                headers.update(api_config.get("default_headers", {}))
            
            # Make request
            response = requests.request(
                method=method,
                url=endpoint,
                headers=headers,
                json=data if method in ["POST", "PUT", "PATCH"] else None,
                params=data if method == "GET" else None,
                timeout=30
            )
            
            return {
                "status": "success",
                "response_status": response.status_code,
                "response_data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "api_name": api_name,
                "endpoint": endpoint
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "api_name": api_name,
                "endpoint": endpoint
            }
    
    # Workflow automation methods
    async def _execute_workflow(self, workflow_name: str, workflow_steps: List[Dict[str, Any]], trigger_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with multiple steps"""
        try:
            results = []
            
            for i, step in enumerate(workflow_steps):
                step_type = step.get("type")
                step_data = step.get("data", {})
                
                # Execute step based on type
                if step_type == "action":
                    result = await self._execute_action(step_data)
                elif step_type == "notification":
                    result = await self._send_notification(step_data)
                elif step_type == "api_call":
                    result = await self._api_integration(step_data)
                else:
                    result = {"status": "unknown_step_type", "step_type": step_type}
                
                results.append({
                    "step_index": i,
                    "step_type": step_type,
                    "result": result
                })
                
                # Check if workflow should continue
                if result.get("status") == "error" and step.get("stop_on_error", True):
                    break
            
            return {
                "status": "completed",
                "workflow_name": workflow_name,
                "steps_executed": len(results),
                "step_results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "workflow_name": workflow_name
            }
    
    # Message handling methods
    async def _handle_action_request(self, message: Message) -> Optional[Message]:
        """Handle action requests from other agents"""
        content = message.content
        action_type = content.get("action_type")
        action_data = content.get("action_data", {})
        
        try:
            result = await self._execute_action({
                "action_type": action_type,
                "action_data": action_data
            })
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="action_response",
                content=result,
                correlation_id=message.id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Action request handling failed",
                action_type=action_type,
                error=str(e),
                agent_id=self.agent_id
            )
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="action_response",
                content={"error": str(e)},
                correlation_id=message.id
            )
            
            return response
    
    async def _handle_notification_request(self, message: Message) -> Optional[Message]:
        """Handle notification requests from other agents"""
        content = message.content
        notification_type = content.get("notification_type", "email")
        recipients = content.get("recipients", [])
        message_text = content.get("message", "")
        subject = content.get("subject", "AI Business Intelligence Notification")
        
        try:
            result = await self._send_notification({
                "notification_type": notification_type,
                "recipients": recipients,
                "message": message_text,
                "subject": subject
            })
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="notification_response",
                content=result,
                correlation_id=message.id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Notification request handling failed",
                notification_type=notification_type,
                error=str(e),
                agent_id=self.agent_id
            )
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="notification_response",
                content={"error": str(e)},
                correlation_id=message.id
            )
            
            return response
    
    async def _handle_report_request(self, message: Message) -> Optional[Message]:
        """Handle report requests from other agents"""
        content = message.content
        report_type = content.get("report_type", "standard")
        report_data = content.get("report_data", {})
        format_type = content.get("format", "json")
        
        try:
            result = await self._generate_report({
                "report_type": report_type,
                "report_data": report_data,
                "format": format_type
            })
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="report_response",
                content=result,
                correlation_id=message.id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Report request handling failed",
                report_type=report_type,
                error=str(e),
                agent_id=self.agent_id
            )
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="report_response",
                content={"error": str(e)},
                correlation_id=message.id
            )
            
            return response
    
    # Utility methods
    def _initialize_notification_templates(self):
        """Initialize notification templates"""
        self.notification_templates = {
            "default": """
Subject: {subject}

{message}

---
Generated by {system_name} at {timestamp}
            """,
            "alert": """
🚨 ALERT: {subject}

{message}

Priority: High
Generated: {timestamp}
System: {system_name}
            """,
            "summary": """
📊 Summary Report: {subject}

{message}

Report generated: {timestamp}
System: {system_name}
            """
        }
    
    def get_action_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent action history"""
        return self.action_history[-limit:]
    
    def get_execution_status(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status of a specific action"""
        return self.execution_status.get(action_id)


# Factory function to create action executor agent
def create_action_executor_agent(agent_id: str = None) -> ActionExecutorAgent:
    """Create and return a new Action Executor Agent instance"""
    return ActionExecutorAgent(agent_id) 