#!/usr/bin/env python3
"""
CHIMERA AUTARCH - New Features Demo
Demonstrates the new tools, intent patterns, and APIs added in v2.1
"""
import requests
import json
import time

CHIMERA_BASE_URL = "http://localhost:3000"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def demo_json_metrics():
    """Demo: JSON metrics endpoint"""
    print_section("1. JSON Metrics API")

    try:
        response = requests.get(f"{CHIMERA_BASE_URL}/metrics", timeout=5)
        data = response.json()

        print(f"Node Count: {data['node_count']}")
        print(f"System Confidence: {data['system_confidence']:.2%}")
        print(f"Active Topics: {', '.join(data['active_topics']) or 'None'}")
        print(f"\nTool Performance:")
        for tool, metrics in list(data['tool_performance'].items())[:5]:
            success_rate = metrics.get('success_rate', 1.0)
            print(f"  - {tool}: {success_rate:.1%} success rate")

    except Exception as e:
        print(f"âŒ Error: {e}")


def demo_prometheus_metrics():
    """Demo: Prometheus metrics endpoint"""
    print_section("2. Prometheus Metrics API")

    try:
        response = requests.get(
            f"{CHIMERA_BASE_URL}/metrics/prometheus", timeout=5)
        lines = response.text.split('\n')

        print("Sample metrics (first 20 lines):")
        for line in lines[:20]:
            if line and not line.startswith('#'):
                print(f"  {line}")

    except Exception as e:
        print(f"âŒ Error: {e}")


def demo_health_check():
    """Demo: Health check endpoint"""
    print_section("3. Health Check API")

    try:
        response = requests.get(f"{CHIMERA_BASE_URL}/api/health", timeout=5)
        data = response.json()

        print(f"Status: {data['status'].upper()}")
        print(f"Checks:")
        for check, status in data['checks'].items():
            emoji = "âœ…" if status == "ok" else "âš ï¸" if status == "warning" else "âŒ"
            print(f"  {emoji} {check}: {status}")

    except Exception as e:
        print(f"âŒ Error: {e}")


def demo_graphql_system_status():
    """Demo: GraphQL system status query"""
    print_section("4. GraphQL - System Status")

    query = """
    {
      systemStatus {
        uptime
        nodeCount
        confidence
        activeTopics
      }
    }
    """

    try:
        response = requests.post(
            f"{CHIMERA_BASE_URL}/graphql",
            json={'query': query},
            timeout=5
        )
        data = response.json()

        if 'errors' in data:
            print(f"âŒ GraphQL Error: {data['errors']}")
            return

        status = data['data']['systemStatus']
        print(f"Uptime: {status['uptime']:.2f} seconds")
        print(f"Node Count: {status['nodeCount']}")
        print(f"Confidence: {status['confidence']:.2%}")
        print(f"Active Topics: {', '.join(status['activeTopics']) or 'None'}")

    except Exception as e:
        print(f"âŒ Error: {e}")


def demo_graphql_tools():
    """Demo: GraphQL tools query"""
    print_section("5. GraphQL - Tools List")

    query = """
    {
      tools {
        name
        version
        description
        successRate
        avgLatency
      }
    }
    """

    try:
        response = requests.post(
            f"{CHIMERA_BASE_URL}/graphql",
            json={'query': query},
            timeout=5
        )
        data = response.json()

        if 'errors' in data:
            print(f"âŒ GraphQL Error: {data['errors']}")
            return

        tools = data['data']['tools']
        print(f"Total Tools: {len(tools)}\n")

        for tool in tools[:8]:  # Show first 8 tools
            print(f"ðŸ“¦ {tool['name']} v{tool['version']}")
            print(f"   {tool['description']}")
            print(f"   Success Rate: {tool['successRate']:.1%}")
            print(f"   Avg Latency: {tool['avgLatency']:.4f}s\n")

    except Exception as e:
        print(f"âŒ Error: {e}")


def demo_graphql_topics():
    """Demo: GraphQL topics query"""
    print_section("6. GraphQL - Topics")

    query = """
    {
      topics {
        name
        confidence
        failureCount
        successRate
      }
    }
    """

    try:
        response = requests.post(
            f"{CHIMERA_BASE_URL}/graphql",
            json={'query': query},
            timeout=5
        )
        data = response.json()

        if 'errors' in data:
            print(f"âŒ GraphQL Error: {data['errors']}")
            return

        topics = data['data']['topics']

        if not topics:
            print("No topics found yet. Topics are created when failures are logged.")
            return

        print(f"Total Topics: {len(topics)}\n")

        for topic in topics:
            print(f"ðŸŽ¯ {topic['name']}")
            print(f"   Confidence: {topic['confidence']:.2%}")
            print(f"   Failures: {topic['failureCount']}")
            print(f"   Success Rate: {topic['successRate']:.1%}\n")

    except Exception as e:
        print(f"âŒ Error: {e}")


def demo_graphql_evolutions():
    """Demo: GraphQL evolutions query"""
    print_section("7. GraphQL - Recent Evolutions")

    query = """
    {
      evolutions(limit: 5) {
        topic
        failureReason
        appliedFix
        observedImprovement
        timestamp
      }
    }
    """

    try:
        response = requests.post(
            f"{CHIMERA_BASE_URL}/graphql",
            json={'query': query},
            timeout=5
        )
        data = response.json()

        if 'errors' in data:
            print(f"âŒ GraphQL Error: {data['errors']}")
            return

        evolutions = data['data']['evolutions']

        if not evolutions:
            print("No evolutions recorded yet.")
            print("Evolutions are created when the system learns from failures.")
            return

        print(f"Showing {len(evolutions)} most recent evolutions:\n")

        for evo in evolutions:
            timestamp = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(evo['timestamp']))
            print(f"ðŸ”„ [{timestamp}] {evo['topic']}")
            print(f"   Issue: {evo['failureReason']}")
            print(f"   Fix: {evo['appliedFix']}")
            print(f"   Improvement: {evo['observedImprovement']:+.2%}\n")

    except Exception as e:
        print(f"âŒ Error: {e}")


def main():
    """Run all demonstrations"""
    print("\n" + "ðŸ”®"*30)
    print("  CHIMERA AUTARCH v2.1 - New Features Demo")
    print("ðŸ”®"*30)

    print(f"\nConnecting to: {CHIMERA_BASE_URL}")
    print("Make sure CHIMERA is running (python chimera_autarch.py)\n")

    input("Press Enter to start the demo...")

    # Run demos in sequence
    demo_json_metrics()
    input("\nPress Enter to continue...")

    demo_prometheus_metrics()
    input("\nPress Enter to continue...")

    demo_health_check()
    input("\nPress Enter to continue...")

    demo_graphql_system_status()
    input("\nPress Enter to continue...")

    demo_graphql_tools()
    input("\nPress Enter to continue...")

    demo_graphql_topics()
    input("\nPress Enter to continue...")

    demo_graphql_evolutions()

    print("\n" + "="*60)
    print("  Demo Complete! ðŸŽ‰")
    print("="*60)
    print("\nNext steps:")
    print("  1. Visit http://localhost:3000/graphql for interactive queries")
    print("  2. Try natural language commands via ws_client.py:")
    print("     - 'show system stats'")
    print("     - 'read file config.yaml'")
    print("     - 'list directory tests'")
    print("  3. Set up Prometheus to scrape /metrics/prometheus")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nâŒ Unexpected error: {e}")
        print("Make sure CHIMERA is running on http://localhost:3000")

