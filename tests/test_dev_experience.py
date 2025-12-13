import asyncio
from src.chimera.core import HeartNode, PersistenceLayer

async def test_dev_experience():
    try:
        # Initialize core
        persistence = PersistenceLayer()
        await persistence.init()
        heart = HeartNode(persistence)

        # Test development report
        result = await heart.dispatch_task('get_development_report', {})
        print('Development Report:', result)

        # Test code analysis
        result = await heart.dispatch_task('run_code_analysis', {'file_path': 'src/chimera/core.py'})
        print('Code Analysis Result:', result.get('status', 'unknown'))

        # Test console command
        result = await heart.dispatch_task('execute_console_command', {'command': 'print("Hello from dev console")'})
        print('Console Command Result:', result)

        print('Developer Experience validation: PASSED')

    except Exception as e:
        print(f'Developer Experience validation: FAILED - {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dev_experience())