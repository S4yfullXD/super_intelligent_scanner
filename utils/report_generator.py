#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Report Generator dengan Color Integration & Advanced Analytics
Professional reporting system dengan comprehensive scan analysis
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
import html

# Import our color system
from .colors import term, success, error, warning, info, debug


class ReportGenerator:
    def __init__(self):
        self.template = self.load_html_template()

    def generate_html_report(self, scan_results: Dict, output_dir: str) -> str:
        """Generate comprehensive HTML report dengan enhanced analytics"""
        print(info("Generating comprehensive HTML report..."))

        try:
            report_data = self.prepare_report_data(scan_results)

            html_content = self.template.format(
                scan_title=report_data["scan_title"],
                scan_date=report_data["scan_date"],
                summary_stats=self.generate_summary_html(report_data["summary"]),
                findings_section=self.generate_findings_html(report_data["findings"]),
                intelligence_section=self.generate_intelligence_html(
                    report_data["intelligence"]
                ),
                recommendations_section=self.generate_recommendations_html(
                    report_data["recommendations"]
                ),
                technical_details=self.generate_technical_details(scan_results),
            )

            report_path = os.path.join(output_dir, "detailed_report.html")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(success(f"HTML report generated: {report_path}"))
            return report_path

        except Exception as e:
            print(error(f"HTML report generation failed: {e}"))
            raise

    def generate_json_report(self, scan_results: Dict, output_dir: str) -> str:
        """Generate detailed JSON report"""
        print(info("Generating JSON report..."))

        try:
            report_data = self.prepare_report_data(scan_results)
            report_path = os.path.join(output_dir, "scan_report.json")

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(success(f"JSON report generated: {report_path}"))
            return report_path

        except Exception as e:
            print(error(f"JSON report generation failed: {e}"))
            raise

    def prepare_report_data(self, scan_results: Dict) -> Dict[str, Any]:
        """Prepare comprehensive data for report generation"""
        print(debug("Preparing report data..."))

        target_url = scan_results.get("target_url", "Unknown")
        successful_finds = scan_results.get("successful_finds", 0)
        total_paths = scan_results.get("total_paths_scanned", 0)

        # Calculate success rate
        success_rate = (
            (successful_finds / total_paths * 100) if total_paths > 0 else 0
        )

        return {
            "scan_title": f"Security Scan Report - {target_url}",
            "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scan_timestamp": scan_results.get(
                "scan_timestamp", int(time.time())
            ),
            "summary": {
                "target_url": target_url,
                "total_paths_scanned": total_paths,
                "successful_finds": successful_finds,
                "saved_files": scan_results.get("saved_files", 0),
                "scan_duration": f"{scan_results.get('scan_duration', 0):.2f} seconds",
                "errors_count": scan_results.get("errors_count", 0),
                "success_rate": f"{success_rate:.1f}%",
            },
            "findings": self.extract_findings(scan_results),
            "intelligence": self.extract_intelligence(scan_results),
            "recommendations": self.generate_recommendations(scan_results),
            "technical_details": self.extract_technical_details(scan_results),
        }

    def extract_findings(self, scan_results: Dict) -> Dict[str, List]:
        """Extract comprehensive findings from scan results"""
        findings: Dict[str, List] = {
            "secrets_found": [],
            "endpoints_discovered": [],
            "files_saved": [],
            "technologies_detected": [],
            "sensitive_paths": [],
            "security_issues": [],
        }

        # Extract from successful paths
        successful_paths = scan_results.get("successful_paths", [])
        findings["files_saved"] = successful_paths[:50]  # Limit untuk report

        # Extract sensitive paths
        findings["sensitive_paths"] = [
            path for path in successful_paths if self.is_sensitive_path(path)
        ][:20]  # Limit untuk report

        # Extract from intelligence data
        intel_data = scan_results.get("intelligence_data", {})

        findings["secrets_found"] = intel_data.get("secrets_found", [])[:10]
        findings["technologies_detected"] = intel_data.get(
            "technologies_detected", []
        )[:15]

        # Extract endpoints from various sources
        endpoints = set()
        endpoints.update(intel_data.get("endpoints_analyzed", []))

        # Add API-like paths from successful finds
        api_paths = [
            p
            for p in successful_paths
            if any(
                api_indicator in p.lower()
                for api_indicator in ["/api/", "/v1/", "/v2/", "/graphql", "/rest/"]
            )
        ]
        endpoints.update(api_paths)

        findings["endpoints_discovered"] = list(endpoints)[:20]

        # Generate security issues
        findings["security_issues"] = self.identify_security_issues(scan_results)

        return findings

    def extract_intelligence(self, scan_results: Dict) -> Dict[str, Any]:
        """Extract comprehensive intelligence data"""
        intelligence: Dict[str, Any] = {
            "content_analysis": {},
            "pattern_analysis": {},
            "risk_assessment": {},
            "performance_metrics": {},
        }

        successful_paths = scan_results.get("successful_paths", [])
        intel_data = scan_results.get("intelligence_data", {})

        # Content analysis
        intelligence["content_analysis"] = {
            "total_files_analyzed": len(successful_paths),
            "file_types_found": self.analyze_file_types(successful_paths),
            "content_categories": self.analyze_content_categories(successful_paths),
            "largest_file_type": self.find_largest_file_type(successful_paths),
        }

        # Risk assessment
        risk_data = intel_data.get("risk_assessment", {})
        intelligence["risk_assessment"] = {
            "secrets_exposed": len(intel_data.get("secrets_found", [])),
            "sensitive_endpoints": len(
                [p for p in successful_paths if self.is_sensitive_path(p)]
            ),
            "overall_risk_level": risk_data.get(
                "overall_risk_level", self.calculate_risk_level(scan_results)
            ),
            "confidence_score": risk_data.get("confidence_score", 0.0),
        }

        # Pattern analysis
        pattern_data = intel_data.get("pattern_analysis", {})
        intelligence["pattern_analysis"] = {
            "common_patterns": pattern_data.get("common_patterns", []),
            "anomalies_detected": pattern_data.get("anomalies", []),
            "architecture_insights": pattern_data.get("architecture", []),
        }

        # Performance metrics
        intelligence["performance_metrics"] = {
            "scan_efficiency": self.calculate_scan_efficiency(scan_results),
            "resource_utilization": self.analyze_resource_usage(scan_results),
            "coverage_metrics": self.calculate_coverage_metrics(scan_results),
        }

        return intelligence

    def extract_technical_details(self, scan_results: Dict) -> Dict[str, Any]:
        """Extract technical implementation details"""
        config = scan_results.get("config_used", {})

        return {
            "scanner_config": {
                "max_workers": config.get("scanning", {}).get(
                    "max_workers", "N/A"
                ),
                "timeout": config.get("scanning", {}).get("timeout", "N/A"),
                "stealth_mode": config.get("evasion", {}).get(
                    "stealth_mode", False
                ),
                "ml_enabled": config.get("intelligence", {}).get(
                    "enable_ml", False
                ),
            },
            "scan_metadata": {
                "start_time": scan_results.get("scan_timestamp", "N/A"),
                "total_duration": scan_results.get("scan_duration", "N/A"),
                "paths_per_second": self.calculate_scan_speed(scan_results),
            },
        }

    def analyze_file_types(self, paths: List[str]) -> Dict[str, int]:
        """Analyze file types from paths dengan enhanced categorization"""
        file_types: Dict[str, int] = {}
        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if not ext:
                ext = "no_extension"
            file_types[ext] = file_types.get(ext, 0) + 1
        return dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True))

    def analyze_content_categories(self, paths: List[str]) -> Dict[str, int]:
        """Analyze content categories"""
        categories: Dict[str, int] = {
            "API Endpoints": 0,
            "JavaScript": 0,
            "HTML Pages": 0,
            "Config Files": 0,
            "Stylesheets": 0,
            "Other": 0,
        }

        for path in paths:
            lower = path.lower()
            if any(
                api_indicator in lower
                for api_indicator in ["/api/", "/v1/", "/v2/", "/graphql"]
            ):
                categories["API Endpoints"] += 1
            elif path.endswith((".js", ".jsx", ".ts", ".tsx")):
                categories["JavaScript"] += 1
            elif path.endswith((".html", ".htm")):
                categories["HTML Pages"] += 1
            elif any(
                config_indicator in lower
                for config_indicator in [".env", "config", "settings"]
            ):
                categories["Config Files"] += 1
            elif path.endswith(".css"):
                categories["Stylesheets"] += 1
            else:
                categories["Other"] += 1

        return {k: v for k, v in categories.items() if v > 0}

    def find_largest_file_type(self, paths: List[str]) -> str:
        """Find the most common file type"""
        file_types = self.analyze_file_types(paths)
        return max(file_types.items(), key=lambda x: x[1], default=("none", 0))[0]

    def is_sensitive_path(self, path: str) -> bool:
        """Enhanced sensitive path detection"""
        sensitive_indicators = [
            ".env",
            "config",
            "secret",
            "password",
            "key",
            "token",
            "admin",
            "database",
            "backup",
            "log",
            "credential",
        ]
        path_lower = path.lower()
        return any(indicator in path_lower for indicator in sensitive_indicators)

    def calculate_risk_level(self, scan_results: Dict) -> str:
        """Calculate overall risk level dengan enhanced logic"""
        secrets_count = len(
            scan_results.get("intelligence_data", {}).get("secrets_found", [])
        )
        sensitive_paths = len(
            [
                p
                for p in scan_results.get("successful_paths", [])
                if self.is_sensitive_path(p)
            ]
        )

        if secrets_count > 0:
            return "CRITICAL"
        elif sensitive_paths > 5:
            return "HIGH"
        elif sensitive_paths > 2:
            return "MEDIUM"
        elif sensitive_paths > 0:
            return "LOW"
        else:
            return "MINIMAL"

    def identify_security_issues(self, scan_results: Dict) -> List[str]:
        """Identify potential security issues"""
        issues: List[str] = []
        intel_data = scan_results.get("intelligence_data", {})

        # Check for exposed secrets
        if intel_data.get("secrets_found"):
            issues.append(
                f"Exposed secrets detected: {len(intel_data['secrets_found'])} items"
            )

        # Check for sensitive file exposure
        sensitive_files = [
            p
            for p in scan_results.get("successful_paths", [])
            if self.is_sensitive_path(p)
        ]
        if sensitive_files:
            issues.append(
                f"Sensitive files exposed: {len(sensitive_files)} files"
            )

        # Check for API endpoint exposure
        api_endpoints = [
            p
            for p in scan_results.get("successful_paths", [])
            if "/api/" in p
        ]
        if len(api_endpoints) > 10:
            issues.append(
                f"Multiple API endpoints exposed: {len(api_endpoints)} endpoints"
            )

        # Check for configuration files
        config_files = [
            p
            for p in scan_results.get("successful_paths", [])
            if any(cf in p.lower() for cf in [".env", "config.json"])
        ]
        if config_files:
            issues.append(
                f"Configuration files exposed: {len(config_files)} files"
            )

        return issues[:10]  # Limit issues list

    def calculate_scan_efficiency(self, scan_results: Dict) -> Dict[str, Any]:
        """Calculate scan efficiency metrics"""
        total_paths = scan_results.get("total_paths_scanned", 0)
        duration = scan_results.get("scan_duration", 1) or 1
        successful = scan_results.get("successful_finds", 0)

        return {
            "paths_per_second": total_paths / duration if duration > 0 else 0,
            "success_rate": (successful / total_paths * 100)
            if total_paths > 0
            else 0,
            "efficiency_score": min(
                100, (successful / max(1, duration)) * 10
            ),
        }

    def analyze_resource_usage(self, scan_results: Dict) -> Dict[str, Any]:
        """Analyze resource usage metrics"""
        config = scan_results.get("config_used", {})

        return {
            "workers_used": config.get("scanning", {}).get(
                "max_workers", "N/A"
            ),
            "timeout_settings": config.get("scanning", {}).get(
                "timeout", "N/A"
            ),
            "evasion_techniques": sum(
                1
                for k, v in config.get("evasion", {}).items()
                if v is True
            ),
        }

    def calculate_coverage_metrics(self, scan_results: Dict) -> Dict[str, Any]:
        """Calculate coverage metrics"""
        total_paths = scan_results.get("total_paths_scanned", 0)
        successful = scan_results.get("successful_finds", 0)

        return {
            "total_coverage": total_paths,
            "effective_coverage": successful,
            "coverage_ratio": (
                f"{(successful / total_paths * 100):.1f}%"
                if total_paths > 0
                else "0%"
            ),
        }

    def calculate_scan_speed(self, scan_results: Dict) -> str:
        """Calculate scan speed in paths per second"""
        total_paths = scan_results.get("total_paths_scanned", 0)
        duration = scan_results.get("scan_duration", 1) or 1

        speed = total_paths / duration
        return f"{speed:.1f} paths/second"

    def generate_recommendations(self, scan_results: Dict) -> List[Dict[str, str]]:
        """Generate comprehensive security recommendations"""
        recommendations: List[Dict[str, str]] = []
        intel_data = scan_results.get("intelligence_data", {})

        # Secrets exposure
        secrets_count = len(intel_data.get("secrets_found", []))
        if secrets_count > 0:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "message": f"Immediately rotate {secrets_count} exposed credentials and secrets",
                    "action": "Credential rotation and access review",
                }
            )

        # Sensitive file exposure
        sensitive_files = [
            p
            for p in scan_results.get("successful_paths", [])
            if self.is_sensitive_path(p)
        ]
        if sensitive_files:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "message": f"Restrict access to {len(sensitive_files)} sensitive files and directories",
                    "action": "Access control implementation",
                }
            )

        # API security
        api_endpoints = [
            p
            for p in scan_results.get("successful_paths", [])
            if "/api/" in p
        ]
        if api_endpoints:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "message": f"Review security of {len(api_endpoints)} exposed API endpoints",
                    "action": "API security assessment",
                }
            )

        # General recommendations
        total = scan_results.get("total_paths_scanned", 1) or 1
        success_rate = (
            scan_results.get("successful_finds", 0) / total
        ) * 100
        if success_rate > 30:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "message": "Consider implementing stricter file access controls and authentication",
                    "action": "Security hardening",
                }
            )

        # Add positive feedback if no critical issues
        if not any(
            rec["priority"] in ["CRITICAL", "HIGH"] for rec in recommendations
        ):
            recommendations.append(
                {
                    "priority": "LOW",
                    "message": "No critical security issues detected. Maintain current security practices.",
                    "action": "Continuous monitoring",
                }
            )

        return recommendations

    def generate_summary_html(self, summary: Dict) -> str:
        """Generate enhanced summary section HTML"""
        return f"""
        <div class="summary-section">
            <h3>📊 Scan Summary</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">🎯 Target URL:</span>
                    <span class="value">{html.escape(str(summary.get('target_url', 'Unknown')))}</span>
                </div>
                <div class="summary-item">
                    <span class="label">🔍 Paths Scanned:</span>
                    <span class="value">{summary.get('total_paths_scanned', 0)}</span>
                </div>
                <div class="summary-item">
                    <span class="label">✅ Successful Finds:</span>
                    <span class="value">{summary.get('successful_finds', 0)}</span>
                </div>
                <div class="summary-item">
                    <span class="label">📁 Files Saved:</span>
                    <span class="value">{summary.get('saved_files', 0)}</span>
                </div>
                <div class="summary-item">
                    <span class="label">⚡ Success Rate:</span>
                    <span class="value">{summary.get('success_rate', '0%')}</span>
                </div>
                <div class="summary-item">
                    <span class="label">⏱️ Duration:</span>
                    <span class="value">{summary.get('scan_duration', '0 seconds')}</span>
                </div>
                <div class="summary-item">
                    <span class="label">❌ Errors:</span>
                    <span class="value">{summary.get('errors_count', 0)}</span>
                </div>
            </div>
        </div>
        """

    def generate_findings_html(self, findings: Dict) -> str:
        """Generate enhanced findings section HTML"""
        # Secrets found
        secrets_items: List[str] = []
        for secret in findings.get("secrets_found", [])[:10]:
            text = str(secret)
            lower = text.lower()
            secret_class = (
                "critical"
                if ("key" in lower or "token" in lower)
                else "warning"
            )
            secrets_items.append(
                f'<li class="finding-item {secret_class}">🔐 {html.escape(text)}</li>'
            )
        secrets_html = (
            "".join(secrets_items)
            or '<li class="finding-item safe">✅ No secrets found</li>'
        )

        # Endpoints discovered
        endpoints_items: List[str] = []
        for endpoint in findings.get("endpoints_discovered", [])[:10]:
            endpoints_items.append(
                f'<li class="finding-item">🌐 {html.escape(str(endpoint))}</li>'
            )
        endpoints_html = (
            "".join(endpoints_items)
            or '<li class="finding-item">No significant endpoints discovered</li>'
        )

        # Sensitive paths
        sensitive_items: List[str] = []
        for path in findings.get("sensitive_paths", [])[:10]:
            sensitive_items.append(
                f'<li class="finding-item warning">⚠️ {html.escape(str(path))}</li>'
            )
        sensitive_html = (
            "".join(sensitive_items)
            or '<li class="finding-item safe">✅ No sensitive paths exposed</li>'
        )

        # Security issues
        issues_items: List[str] = []
        for issue in findings.get("security_issues", [])[:10]:
            issue_text = str(issue)
            issue_class = (
                "critical" if "exposed" in issue_text.lower() else "warning"
            )
            issues_items.append(
                f'<li class="finding-item {issue_class}">🚨 {html.escape(issue_text)}</li>'
            )
        issues_html = (
            "".join(issues_items)
            or '<li class="finding-item safe">✅ No critical security issues</li>'
        )

        return f"""
        <div class="findings-section">
            <h3>🔍 Detailed Findings</h3>

            <div class="finding-category">
                <h4>🔐 Secrets Found ({len(findings.get('secrets_found', []))}):</h4>
                <ul class="findings-list">{secrets_html}</ul>
            </div>

            <div class="finding-category">
                <h4>⚠️ Sensitive Paths ({len(findings.get('sensitive_paths', []))}):</h4>
                <ul class="findings-list">{sensitive_html}</ul>
            </div>

            <div class="finding-category">
                <h4>🚨 Security Issues ({len(findings.get('security_issues', []))}):</h4>
                <ul class="findings-list">{issues_html}</ul>
            </div>

            <div class="finding-category">
                <h4>🌐 Endpoints Discovered ({len(findings.get('endpoints_discovered', []))}):</h4>
                <ul class="findings-list">{endpoints_html}</ul>
            </div>
        </div>
        """

    def generate_intelligence_html(self, intelligence: Dict) -> str:
        """Generate enhanced intelligence section HTML"""
        risk_level = intelligence.get("risk_assessment", {}).get(
            "overall_risk_level", "UNKNOWN"
        )
        risk_class = f"risk-{str(risk_level).lower()}"

        # File types analysis
        file_types = intelligence.get("content_analysis", {}).get(
            "file_types_found", {}
        )
        file_types_items: List[str] = []
        for ext, count in list(file_types.items())[:10]:
            file_types_items.append(
                f"<li>{html.escape(str(ext))}: {count} files</li>"
            )
        file_types_html = (
            "".join(file_types_items)
            or "<li>No file type analysis available</li>"
        )

        # Performance metrics
        perf = intelligence.get("performance_metrics", {}).get(
            "scan_efficiency", {}
        )
        efficiency_html = f"""
            <p>Scan Speed: <strong>{float(perf.get('paths_per_second', 0)):.1f} paths/sec</strong></p>
            <p>Success Rate: <strong>{float(perf.get('success_rate', 0)):.1f}%</strong></p>
            <p>Efficiency Score: <strong>{float(perf.get('efficiency_score', 0)):.1f}/100</strong></p>
        """

        risk_assessment = intelligence.get("risk_assessment", {})
        content_analysis = intelligence.get("content_analysis", {})

        return f"""
        <div class="intelligence-section">
            <h3>🧠 Intelligence Analysis</h3>

            <div class="intel-category">
                <h4>📈 Risk Assessment:</h4>
                <p>Overall Risk Level: <strong class="{risk_class}">{risk_level}</strong></p>
                <p>Secrets Exposed: <strong>{risk_assessment.get('secrets_exposed', 0)}</strong></p>
                <p>Sensitive Endpoints: <strong>{risk_assessment.get('sensitive_endpoints', 0)}</strong></p>
                <p>Confidence Score: <strong>{float(risk_assessment.get('confidence_score', 0)):.1f}/10</strong></p>
            </div>

            <div class="intel-category">
                <h4>📊 Content Analysis:</h4>
                <p>Total Files Analyzed: <strong>{content_analysis.get('total_files_analyzed', 0)}</strong></p>
                <p>Largest File Type: <strong>{content_analysis.get('largest_file_type', 'N/A')}</strong></p>
                <ul>{file_types_html}</ul>
            </div>

            <div class="intel-category">
                <h4>⚡ Performance Metrics:</h4>
                {efficiency_html}
            </div>
        </div>
        """

    def generate_recommendations_html(self, recommendations: List[Dict]) -> str:
        """Generate enhanced recommendations section HTML"""
        items: List[str] = []
        for rec in recommendations:
            priority = rec.get("priority", "LOW")
            message = rec.get("message", "")
            action = rec.get("action", "")
            items.append(
                f'''
            <li class="recommendation {priority.lower()}">
                <div class="rec-header">
                    <span class="priority-badge {priority.lower()}">{priority}</span>
                    <strong>{html.escape(str(message))}</strong>
                </div>
                <div class="rec-action">💡 Action: {html.escape(str(action))}</div>
            </li>
            '''
            )

        rec_html = "".join(items)

        return f"""
        <div class="recommendations-section">
            <h3>💡 Security Recommendations</h3>
            <ul class="recommendations-list">{rec_html}</ul>
        </div>
        """

    def generate_technical_details(self, scan_results: Dict) -> str:
        """Generate technical details section"""
        tech_details = self.extract_technical_details(scan_results)

        return f"""
        <div class="technical-section">
            <h3>🔧 Technical Details</h3>
            <div class="tech-grid">
                <div class="tech-category">
                    <h4>Scanner Configuration</h4>
                    <p>Max Workers: <strong>{tech_details['scanner_config']['max_workers']}</strong></p>
                    <p>Timeout: <strong>{tech_details['scanner_config']['timeout']}s</strong></p>
                    <p>Stealth Mode: <strong>{'Enabled' if tech_details['scanner_config']['stealth_mode'] else 'Disabled'}</strong></p>
                    <p>ML Features: <strong>{'Enabled' if tech_details['scanner_config']['ml_enabled'] else 'Disabled'}</strong></p>
                </div>
                <div class="tech-category">
                    <h4>Scan Metadata</h4>
                    <p>Scan Speed: <strong>{tech_details['scan_metadata']['paths_per_second']}</strong></p>
                    <p>Total Duration: <strong>{tech_details['scan_metadata']['total_duration']}</strong></p>
                </div>
            </div>
        </div>
        """

    def load_html_template(self) -> str:
        """Load enhanced HTML report template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{scan_title}</title>
    <style>
        /* Enhanced CSS styles would be here */
        /* ... (keeping your original CSS and adding new classes) */
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0b1120;
            color: #e5e7eb;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 32px;
        }}
        .summary-section, .findings-section, .intelligence-section,
        .recommendations-section, .technical-section {{
            background: #020617;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            border: 1px solid #1f2937;
        }}
        .summary-grid, .tech-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }}
        .summary-item, .tech-category, .finding-category, .intel-category {{
            background: #020617;
            border-radius: 8px;
            padding: 12px;
            border: 1px solid #1f2937;
        }}
        .label {{
            color: #9ca3af;
            font-size: 0.9rem;
        }}
        .value {{
            font-weight: 600;
            display: block;
        }}
        .findings-list, .recommendations-list {{
            list-style: none;
            padding-left: 0;
            margin: 8px 0 0 0;
        }}
        .finding-item {{
            padding: 6px 8px;
            border-radius: 6px;
            margin-bottom: 4px;
            border: 1px solid #1f2937;
        }}
        .finding-item.critical {{
            border-color: #f97373;
            background: rgba(248, 113, 113, 0.1);
        }}
        .finding-item.warning {{
            border-color: #facc15;
            background: rgba(250, 204, 21, 0.08);
        }}
        .finding-item.safe {{
            border-color: #22c55e;
            background: rgba(34, 197, 94, 0.08);
        }}
        .risk-critical {{ color: #f97373; }}
        .risk-high {{ color: #f97316; }}
        .risk-medium {{ color: #eab308; }}
        .risk-low {{ color: #22c55e; }}
        .risk-minimal {{ color: #22c55e; }}
        .priority-badge {{
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 0.75rem;
            text-transform: uppercase;
            margin-right: 8px;
        }}
        .priority-badge.critical {{ background: #b91c1c; color: #fee2e2; }}
        .priority-badge.high {{ background: #ca8a04; color: #fef9c3; }}
        .priority-badge.medium {{ background: #0369a1; color: #e0f2fe; }}
        .priority-badge.low {{ background: #15803d; color: #dcfce7; }}
        .recommendation {{
            padding: 8px 10px;
            border-radius: 8px;
            border: 1px solid #1f2937;
            margin-bottom: 6px;
        }}
        .rec-header {{
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }}
        .rec-action {{
            font-size: 0.9rem;
            color: #9ca3af;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{scan_title}</h1>
        <p>Generated on: {scan_date}</p>
    </div>

    {summary_stats}
    {findings_section}
    {intelligence_section}
    {recommendations_section}
    {technical_details}

    <footer style="text-align: center; margin-top: 50px; color: #666;">
        <p>Generated by Super Intelligent Scanner</p>
    </footer>
</body>
</html>
        """


# Test function
def test_report_generator():
    """Test the enhanced report generator"""
    print(term.styles.banner("Testing Report Generator"))

    # Create sample scan results
    sample_results = {
        "target_url": "https://api.example.com",
        "total_paths_scanned": 150,
        "successful_finds": 45,
        "saved_files": 38,
        "scan_duration": 125.5,
        "errors_count": 3,
        "successful_paths": [
            "/api/v1/users",
            "/static/js/main.js",
            "/config.json",
            "/.env",
            "/admin/dashboard",
            "/api/v2/auth",
        ],
        "intelligence_data": {
            "secrets_found": [
                "api_key: xyz123",
                "database_url: postgres://...",
            ],
            "technologies_detected": [
                "React",
                "Node.js",
                "Express",
                "MongoDB",
            ],
            "risk_assessment": {
                "total_secrets": 2,
                "sensitive_files": 3,
                "overall_risk_level": "HIGH",
            },
        },
        "config_used": {
            "scanning": {"max_workers": 10, "timeout": 15},
            "evasion": {"stealth_mode": True},
            "intelligence": {"enable_ml": False},
        },
    }

    # Test report generation
    generator = ReportGenerator()

    try:
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = generator.generate_json_report(sample_results, temp_dir)
            print(success(f"JSON report test passed: {json_path}"))

            html_path = generator.generate_html_report(sample_results, temp_dir)
            print(success(f"HTML report test passed: {html_path}"))

        print(success("Report generator test completed successfully!"))

    except Exception as e:
        print(error(f"Report generator test failed: {e}"))


if __name__ == "__main__":
    test_report_generator()