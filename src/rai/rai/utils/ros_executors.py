# Copyright (C) 2024 Robotec.AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable, Optional, Union

from rclpy.executors import (
    ConditionReachedException,
    ExternalShutdownException,
    MultiThreadedExecutor,
    ShutdownException,
    TimeoutException,
    TimeoutObject,
)


class MultiThreadedExecutorFixed(MultiThreadedExecutor):
    """
    Adresses a comment:
    ```python
    # make a copy of the list that we iterate over while modifying it
    # (https://stackoverflow.com/q/1207406/3753684)
    ```
    from the rclpy implementation
    """

    def _spin_once_impl(
        self,
        timeout_sec: Optional[Union[float, TimeoutObject]] = None,
        wait_condition: Callable[[], bool] = lambda: False,
    ) -> None:
        try:
            handler, entity, node = self.wait_for_ready_callbacks(
                timeout_sec, None, wait_condition
            )
        except ExternalShutdownException:
            pass
        except ShutdownException:
            pass
        except TimeoutException:
            pass
        except ConditionReachedException:
            pass
        else:
            self._executor.submit(handler)
            self._futures.append(handler)
            futures = self._futures.copy()
            for future in futures[:]:
                if future.done():
                    futures.remove(future)
                    future.result()  # raise any exceptions
            self._futures = futures
