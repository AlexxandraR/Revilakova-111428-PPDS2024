# Sources:
# https://docs.aiohttp.org/en/stable/
# https://tqdm.github.io/
# https://pub.aimind.so/download-large-file-in-python-with-beautiful-progress-bar-f4f86b394ad7

import aiohttp
import asyncio
import os
from tqdm import tqdm


async def download_file(session, url, filename):
    async with session.get(url) as response:
        file_size = int(response.headers.get('Content-Length', 0))
        with tqdm(total=file_size, unit='B', unit_scale=True,
                  desc=filename) as progress_bar:
            with open(filename, 'wb') as f:
                async for data in response.content.iter_chunked(1024):
                    f.write(data)
                    progress_bar.update(len(data))


async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            filename = os.path.basename(url)
            task = asyncio.create_task(download_file(session, url,
                                                     filename))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    url_names = [
        'https://ploszek.com/ppds/2024-11.async.pdf',
        'https://ploszek.com/ppds/2024-12.async2.pdf'
    ]
    asyncio.run(main(url_names))
