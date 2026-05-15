import asyncio
import subprocess
import time

async def open_process_and_parse_output(command:list, callback:callable):
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
	await parse_process_output(process, callback)
	
async def parse_process_output(process, callback:callable):
    try:
        for line in process.stdout:
            callback(line)
            await asyncio.sleep(0.001)
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        raise
    finally:
        process.wait()
        process.stdout.close()