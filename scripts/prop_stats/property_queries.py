from typing import Any, Callable, List, Tuple

import time
import re

import asyncio
import aiohttp
# from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

USER_AGENT = {
    'User-Agent':
    'A bot for counting sitelinks for properties. (guszarzmo@student.gu.se)'
}  # noqa:


class RequestStats:
    """
    A class that tracks the statistics of requests.

    Public methods:
    - update_elapsed_time_last() -> None
    - append_elapsed_time(elapsed_time: float) -> None
    - add_request_task(request_id: str) -> float
    - remove_request_task(request_id: str) -> None
    - get_elapsed_time_total() -> float

    Attributes:
    - elapsed_times: A list of elapsed times of finished requests.
    - start_times: A dictionary of start times of ongoing requests.
    - elapsed_time_total_per_60s: A list of total elapsed times in the last 60
      seconds.
    """

    def __init__(self):
        self.start_times = dict()
        self.start_times_lock = asyncio.Lock()

        self.elapsed_times = []
        self.elapsed_times_lock = asyncio.Lock()

        self.elapsed_time_total = [0]

    async def get_elapsed_time(self, update: False) -> float:

        # Calculate the elapsed time for finished requests
        elapsed_times_copy = self.elapsed_times.copy()
        finished_elapsed_time = sum(elapsed_times_copy)
        if update:
            self.elapsed_times.clear()

        # Calculate the elapsed time for running requests
        current_time = time.monotonic()
        running_elapsed_time = sum([
            current_time - start_time
            for start_time in self.start_times.values()
        ])

        # Calculate the total elapsed time
        elapsed_time = running_elapsed_time + finished_elapsed_time

        return elapsed_time

    async def update_elapsed_time_last(self):
        """
        A method that updates elapsed time. This function should be called
        periodically to calculate the elapsed time of the elapsed peroid.
        """
        async with self.elapsed_times_lock:
            async with self.start_times_lock:
                elapsed_time = await self.get_elapsed_time(update=True)
                self.elapsed_time_total.append(elapsed_time)

    async def append_elapsed_time(self, elapsed_time: float):
        """
        A method that save the elapsed time of a finished request.

        Args:
          - elapsed_time: A float representing the elapsed time in seconds.
        """
        async with self.elapsed_times_lock:
            self.elapsed_times.append(elapsed_time)

    async def add_request_task(self, request_id):
        """
        A method that adds the start time of an ongoing request.

        Args:
          - request_id: A string representing the unique ID of the request.

        Return:
          - A float representing the start time of the request.
        """
        async with self.start_times_lock:
            start_time = time.monotonic()
            self.start_times[request_id] = start_time
            return start_time

    async def remove_request_task(self, request_id):
        """
        A method that removes the start time of a finished request.

        Args:
          - request_id: A string representing the unique ID of the request.
        """
        async with self.start_times_lock:
            self.start_times.pop(request_id)

    def get_elapsed_time_total(self) -> List[float]:
        """
        A method that returns the total elapsed time of finished and ongoing
        requests.

        return:
          - A float representing the total elapsed time in seconds.
        """
        return self.elapsed_time_total


async def ticker(interval: float, callback: Callable[..., Any]) -> None:
    while True:
        await asyncio.sleep(interval)
        await callback()


async def fetch_entities(session: aiohttp.ClientSession, url: str,
                         semaphore: asyncio.Semaphore,
                         stats: RequestStats) -> Tuple[List[str], str]:
    """
    Fetches a list of entities from a given API URL.  The function returns the
    list of entities and the value of the "blcontinue" parameter from the
    response JSON, which is used to get the next batch of entities.

    Args:
        - session (aiohttp.ClientSession): An HTTP client session object.
        - url (str): The API URL to fetch entities from.
        - semaphore (asyncio.Semaphore): A semaphore object that limits the
          number of concurrent requests.
        - stats (RequestStats): A RequestStats object that stores the request
          counter and elapsed time list.

    Returns:
        - Tuple[List[str], str]: A tuple containing the list of entities and the
        value of the "blcontinue" parameter.
    """

    # The function uses an HTTP GET request to fetch a JSON response from a
    # Wikidata API URL. It extracts the "title" field from the "backlinks"
    # dictionary in the response to get a list of entities that link to a
    # property. It also extracts the value of the "blcontinue" field in the
    # response JSON, which is used to fetch the next batch of entities. The
    # maximum batch length is 500.
    # The function uses a semaphore object to limit the number of concurrent
    # requests that can be made to the API endpoint.
    async with semaphore:
        # increment request_counter
        request_id = ''.join(
            re.findall(
                r'(?:(?<=&bltitle=Property:)\w+)|(?:(?<=&blcontinue=).+)',
                url))
        start_time = await stats.add_request_task(request_id)

        async with session.get(url, headers=USER_AGENT) as response:
            status = response.status
            if status != 200:
                print(response.status, response.content)
            data = await response.json(content_type=None, encoding='utf-8')

            end_time = time.monotonic()
            elapsed_time = end_time - start_time
            await stats.append_elapsed_time(elapsed_time)
            await stats.remove_request_task(request_id)

            data_list = data['query']['backlinks']
            entities = [entity_dict['title'] for entity_dict in data_list]

            await asyncio.sleep(1.25)
            return entities, data.get('continue', {}).get('blcontinue')


async def get_entites(session: aiohttp.ClientSession, prop_id: str,
                      prop_links_api: str, semaphore: asyncio.Semaphore,
                      stats: RequestStats) -> List[str]:
    """
    Gets a list of entities that link to a given property ID.

    Args:
        - session (aiohttp.ClientSession): An HTTP client session object.
        - prop_id (str): The property ID to get entities that link to it.
        - prop_links_api (str): The URL of the Wikidata API endpoint that gets
          the entities that link to a property.
        - semaphore (asyncio.Semaphore): A semaphore object that limits the
          number of concurrent requests.
        - stats (RequestStats): A RequestStats object that stores the request
          counter and elapsed time list.

    Returns:
        List[str]: A list of entities that link to the given property ID.
    """

    # This function takes a property ID and a Wikidata API endpoint as input and
    # uses the `fetch_entities` function to get a list of entities that link to
    # the property. It uses the `blcontinue` parameter in the API response to
    # fetch the next batch of entities.
    entities = []  # list to store entities
    blcontinue = ''
    url_base = prop_links_api.format(0, 500, prop_id)  # base url
    url = url_base
    # Call fetch_entities with the session, URL, and semaphore, and continue
    # calling it with the blcontinue parameter to get the next batch until no
    # more entities are returned
    counter = 0
    while blcontinue is not None:
        result, blcontinue = await fetch_entities(session, url, semaphore,
                                                  stats)
        entities.extend(result)
        if blcontinue and counter < 10:
            # update url endpoint to get the next batch
            url = url_base + '&blcontinue=' + blcontinue
            counter += 1
        else:
            break

    return entities


async def collect_entities(prop_ids: List[str],
                           prop_links_api: str) -> List[Tuple[str, List[str]]]:
    """
    Collects a list of entities that link to each property ID in a given list
    of property IDs.

    Args:
        - prop_ids (List[str]): A list of property IDs to get entities that
          link to them.
        - prop_links_api (str): The URL of the Wikidata API endpoint that gets
          the entities that link to a property.

    Returns:
        - List[Tuple[str, List[List[str]]]]: The tuple containing:
          - The first element is property ID.
          - The second element is a list entities that link to the
          corresponding property ID in the first element.
    """
    # Define a coroutine function to run the get_entities function
    # asynchronously for each prop_id.
    # The function defines a list of tasks, each of which calls the
    # get_entities function for a single property ID.  The function uses a
    # semaphore object to limit the number of concurrent requests that can be
    # made to the API endpoint. The tasks are then gathered using the
    # `tqdm_asyncio.gather` function which runs them concurrently and returns a
    # list of the results.
    stats = RequestStats()
    tasks = []  # type: List[List[str]]
    # Create a semaphore object with a limit of 5 concurrent requests
    semaphore = asyncio.Semaphore(3)
    async with aiohttp.ClientSession() as session:
        asyncio.create_task(ticker(60.0, stats.update_elapsed_time_last))
        # create tasks list
        for prop_id in prop_ids:
            task = asyncio.create_task(
                get_entites(session, prop_id, prop_links_api, semaphore,
                            stats))
            tasks.append(task)

        all_entities = []
        pbar = tqdm(total=len(tasks))
        for entities in asyncio.as_completed(tasks):
            elapsed_time = stats.elapsed_time_total[-1]
            pbar.set_description(f'Elapsed Time: {elapsed_time:.2f}')
            pbar.update()
            all_entities.append(await entities)

    # Wait for all tasks to complete
    entities_lists = [task._result for task in tasks]

    return list(zip(prop_ids, entities_lists))


def prop_blinks_query(prop_ids: str,
                      output_path: str) -> List[Tuple[str, List[str]]]:
    """
    Collects a list of entities that link to each property ID in a given list
    of property IDs and writes the results to a compressed CSV file using a
    given api endpoint/

    Args:
        - prop_ids (str): A string of property IDs separated by '|'.
        - output_path (str): The path to write the compressed CSV file to.

    Returns:
       - List[Tuple[str, List[List[str]]]]: The tuple containing:
          - The first element is property ID.
          - The second element is a list entities that link to the
          corresponding property ID in the first element.
    """
    # Define the Wikidata API URL for getting entities that link to a property
    prop_links_api = 'https://www.wikidata.org/w/api.php?' \
        'action=query' \
        '&list=backlinks' \
        '&blnamespace={}' \
        '&bllimit={}' \
        '&bltitle=Property:{}' \
        '&format=json' \
        '&formatversion=2'

    # Call the collect_entities function to get the entities that link to each
    # property ID in the input list asynchronously.
    results = asyncio.run(collect_entities(prop_ids, prop_links_api))

    # Write the results to a compressed CSV file
    write_to_parquet(results, output_path)

    return results


def write_to_parquet(data: List[Tuple[str, List[str]]],
                     output_path: str) -> None:

    # Convert list of tuples to DataFrame
    df = pd.DataFrame(data, columns=['property_id', 'entity'])

    # Convert DataFrame to Arrow table
    table = pa.Table.from_pandas(df)

    # Write Arrow table to Parquet file
    pq.write_table(table, output_path)
