#!/usr/bin/env python3
"""
19b - Monitoring Pattern
Simple example showing how to monitor AI agent performance and behavior.

This demonstrates:
1. Performance metrics tracking
2. Real-time monitoring
3. Alert systems
4. Performance reporting
"""

import sys
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class PerformanceMetrics:
    """Track performance metrics for AI agents."""
    
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_response_time": 0,
            "response_times": [],
            "error_types": {},
            "hourly_stats": {},
            "daily_stats": {}
        }
        self.alerts = []
    
    def add_response(self, response_time, success=True, error_type=None):
        """Add a response to metrics tracking."""
        self.metrics["total_queries"] += 1
        self.metrics["response_times"].append(response_time)
        
        if success:
            self.metrics["successful_responses"] += 1
        else:
            self.metrics["failed_responses"] += 1
            if error_type:
                self.metrics["error_types"][error_type] = self.metrics["error_types"].get(error_type, 0) + 1
        
        # Update average response time
        self.metrics["average_response_time"] = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        
        # Update hourly stats
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
        if current_hour not in self.metrics["hourly_stats"]:
            self.metrics["hourly_stats"][current_hour] = {"queries": 0, "success_rate": 0, "avg_time": 0}
        
        self.metrics["hourly_stats"][current_hour]["queries"] += 1
        self.metrics["hourly_stats"][current_hour]["success_rate"] = (
            self.metrics["successful_responses"] / self.metrics["total_queries"] * 100
        )
        self.metrics["hourly_stats"][current_hour]["avg_time"] = self.metrics["average_response_time"]
    
    def check_alerts(self):
        """Check for performance alerts."""
        alerts = []
        
        # Check response time alert
        if self.metrics["average_response_time"] > 5.0:  # 5 seconds threshold
            alerts.append({
                "type": "HIGH_RESPONSE_TIME",
                "message": f"Average response time is {self.metrics['average_response_time']:.2f}s (threshold: 5.0s)",
                "severity": "WARNING"
            })
        
        # Check success rate alert
        if self.metrics["total_queries"] > 0:
            success_rate = (self.metrics["successful_responses"] / self.metrics["total_queries"]) * 100
            if success_rate < 90:  # 90% threshold
                alerts.append({
                    "type": "LOW_SUCCESS_RATE",
                    "message": f"Success rate is {success_rate:.1f}% (threshold: 90%)",
                    "severity": "CRITICAL"
                })
        
        # Check error rate alert
        if self.metrics["total_queries"] > 10:  # Only check after some queries
            error_rate = (self.metrics["failed_responses"] / self.metrics["total_queries"]) * 100
            if error_rate > 10:  # 10% threshold
                alerts.append({
                    "type": "HIGH_ERROR_RATE",
                    "message": f"Error rate is {error_rate:.1f}% (threshold: 10%)",
                    "severity": "WARNING"
                })
        
        self.alerts.extend(alerts)
        return alerts
    
    def get_summary(self):
        """Get summary of performance metrics."""
        success_rate = (self.metrics["successful_responses"] / self.metrics["total_queries"]) * 100 if self.metrics["total_queries"] > 0 else 0
        
        return {
            "total_queries": self.metrics["total_queries"],
            "success_rate": f"{success_rate:.1f}%",
            "average_response_time": f"{self.metrics['average_response_time']:.2f}s",
            "failed_responses": self.metrics["failed_responses"],
            "active_alerts": len(self.alerts)
        }

class AgentMonitor:
    """Monitor AI agent performance and behavior."""
    
    def __init__(self):
        self.llm = get_llm()
        self.metrics = PerformanceMetrics()
        self.session_log = []
        self.start_time = datetime.now()
    
    def process_query(self, query):
        """Process a query and monitor performance."""
        start_time = time.time()
        
        try:
            # Simulate AI response generation
            response = self.llm.generate(query).content
            response_time = time.time() - start_time
            
            # Log the interaction
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "response_time": response_time,
                "status": "success"
            }
            
            self.session_log.append(interaction)
            
            # Update metrics
            self.metrics.add_response(response_time, success=True)
            
            return {
                "response": response,
                "response_time": response_time,
                "status": "success"
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            error_type = type(e).__name__
            
            # Log the error
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": f"Error: {str(e)}",
                "response_time": response_time,
                "status": "error",
                "error_type": error_type
            }
            
            self.session_log.append(interaction)
            
            # Update metrics
            self.metrics.add_response(response_time, success=False, error_type=error_type)
            
            return {
                "response": f"Error: {str(e)}",
                "response_time": response_time,
                "status": "error"
            }
    
    def get_performance_report(self):
        """Generate a comprehensive performance report."""
        summary = self.metrics.get_summary()
        uptime = datetime.now() - self.start_time
        
        report = f"""
📊 Agent Performance Report
==========================
Session Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Uptime: {str(uptime).split('.')[0]}

📈 Performance Metrics:
Total Queries: {summary['total_queries']}
Success Rate: {summary['success_rate']}
Average Response Time: {summary['average_response_time']}
Failed Responses: {summary['failed_responses']}
Active Alerts: {summary['active_alerts']}

📊 Error Breakdown:
"""
        
        for error_type, count in self.metrics.metrics["error_types"].items():
            report += f"- {error_type}: {count}\n"
        
        # Show recent activity
        report += f"\n🕒 Recent Activity (Last 3 queries):\n"
        for interaction in self.session_log[-3:]:
            status_icon = "✅" if interaction["status"] == "success" else "❌"
            report += f"{status_icon} {interaction['timestamp']}: {interaction['query'][:30]}... ({interaction['response_time']:.2f}s)\n"
        
        return report
    
    def get_alerts(self):
        """Get current alerts."""
        alerts = self.metrics.check_alerts()
        if alerts:
            alert_report = "🚨 Active Alerts:\n"
            for alert in alerts:
                severity_icon = "🔴" if alert["severity"] == "CRITICAL" else "🟡"
                alert_report += f"{severity_icon} {alert['severity']}: {alert['message']}\n"
            return alert_report
        else:
            return "✅ No active alerts"
    
    def get_health_status(self):
        """Get overall health status."""
        summary = self.metrics.get_summary()
        
        # Calculate health score
        success_rate = float(summary['success_rate'].replace('%', ''))
        avg_time = float(summary['average_response_time'].replace('s', ''))
        
        health_score = 100
        if success_rate < 95:
            health_score -= 20
        if avg_time > 3:
            health_score -= 15
        if summary['active_alerts'] > 0:
            health_score -= 25
        
        if health_score >= 90:
            status = "🟢 HEALTHY"
        elif health_score >= 70:
            status = "🟡 WARNING"
        else:
            status = "🔴 CRITICAL"
        
        return {
            "status": status,
            "health_score": health_score,
            "summary": summary
        }

def main():
    print("📊 Monitoring Pattern")
    print("=" * 40)
    
    # Initialize monitor
    monitor = AgentMonitor()
    print(f"Using LLM: {monitor.llm.provider}")
    
    # Test queries
    test_queries = [
        "What is the capital of France?",
        "How do I bake a chocolate cake?",
        "Explain quantum computing in simple terms",
        "What are the benefits of renewable energy?",
        "Tell me about machine learning algorithms",
        "Calculate 2 + 2",
        "What's the weather like today?",
        "How do I learn Python programming?"
    ]
    
    print(f"\n--- Processing {len(test_queries)} test queries ---")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query[:40]}... ---")
        
        result = monitor.process_query(query)
        
        print(f"Status: {'✅ Success' if result['status'] == 'success' else '❌ Error'}")
        print(f"Response Time: {result['response_time']:.2f}s")
        print(f"Response: {result['response'][:80]}...")
        
        # Check for alerts every few queries
        if i % 3 == 0:
            alerts = monitor.metrics.check_alerts()
            if alerts:
                print(f"🚨 New Alerts: {len(alerts)}")
    
    # Generate reports
    print(f"\n--- Performance Report ---")
    report = monitor.get_performance_report()
    print(report)
    
    print(f"\n--- Alert Status ---")
    alerts = monitor.get_alerts()
    print(alerts)
    
    print(f"\n--- Health Status ---")
    health = monitor.get_health_status()
    print(f"Status: {health['status']}")
    print(f"Health Score: {health['health_score']}/100")
    
    print(f"\n--- Monitoring Pattern Summary ---")
    print(f"✅ Demonstrated performance metrics tracking")
    print(f"✅ Showed real-time monitoring")
    print(f"✅ Implemented alert system")
    print(f"✅ Created health status monitoring")

if __name__ == "__main__":
    main()
