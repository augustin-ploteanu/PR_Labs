# Laboratory 2 Report

## Starting the Container

Inside the Lab2 folder execute the following commands to build and start the server container:

```bash
docker compose build tester
docker compose up single threaded
```

---

## Performance comparison

In another terminal run:

```bash
docker compose run --rm tester
```

Single threaded:

![img1](/Lab2/screenshots/img1.png)

Multithreaded:

![img2](/Lab2/screenshots/img2.png)

---

## Hit counter and race condition

The race condition was triggered with the use of **test.py** by running 50 parallel requests against the same file on the multithreaded server after removing the lock around the hit counter.

Responsible code:

```python
current = hit_count[str(fs_path)]
time.sleep(0.05)   
hit_count[str(fs_path)] = current + 1
```

![img3](/Lab2/screenshots/img3.png)

Fixed code:

```python
with hit_lock:
      hit_count[str(fs_path)] += 1
```

![img4](/Lab2/screenshots/img4.png)

---

## Rate limiting

Given that the rate limiter has 5 requests/sec per IP:

![img5](/Lab2/screenshots/img5.png)


---

##  IP Awarness

To demonstrate per-IP rate limiting two clients concurrently against the multithreaded server using the **rate_test_ip.py** script. Client A (run inside a Docker container) requested the content directory and exceeded the limit, receiving mostly 429 Too Many Requests responses, while Client B (run from the host machine) requested a png file and consistently received 200 OK responses.

![img6](/Lab2/screenshots/img6.png)
