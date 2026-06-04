# Section C - Scalability & Problem Solving

## Scenario

* 1000 internships are published.
* 50,000 students apply within 1 hour.

---

## 1. How will the system handle this traffic?

The system will use a scalable architecture consisting of:

* Load Balancer (NGINX)
* Multiple Django DRF API instances
* Use PostgreSQL with proper indexing.
* Cache frequently accessed internship data in Redis.
* Move heavy operations (emails, notifications, analytics) to background workers.
* Use horizontal scaling when traffic increases.

Architecture:

```text
Clients
   |
Load Balancer
   |
---------------------
|        |         |
API-1   API-2    API-3
   |
Redis Cache
   |
PostgreSQL
   |
RabbitMQ
   |
Celery Workers
```

This architecture distributes requests across multiple servers and prevents a single point of failure.

---

## 2. How will duplicate applications be prevented?

### Application-Level Validation

Before creating an application, the system checks whether the student has already applied.

```python
Application.objects.filter(
    student=user,
    internship=internship
).exists()
```

### Database-Level Protection

A unique constraint is added:

```sql
UNIQUE(student_id, internship_id)
```

This guarantees that duplicate applications cannot be inserted even during concurrent requests.

---

## 3. How will response time stay below 500ms?

The following optimizations will be used:

* Redis caching for internship listings
* Database indexing
* Pagination
* Query optimization
* select_related() and prefetch_related()
* Background task processing

Example:

```python
Internship.objects.select_related("company")
```

This minimizes unnecessary database queries and improves response time.

---

## 4. What indexes will be created?

### Users

```sql
CREATE INDEX idx_users_email
ON users(email);
```

### Internships

```sql
CREATE INDEX idx_internship_company
ON internships(company_id);
```

### Applications

```sql
CREATE INDEX idx_application_student
ON applications(student_id);

CREATE INDEX idx_application_internship
ON applications(internship_id);
```

### Composite Index

```sql
CREATE UNIQUE INDEX idx_student_internship
ON applications(student_id, internship_id);
```

---

## 5. Will Redis be used?

Yes.

Redis will be used for:

* Internship listing cache
* Dashboard statistics
* Frequently accessed data
* Rate limiting

Benefits:

* Faster responses
* Reduced database load
* Improved scalability

---

## 6. Will Queue Systems (RabbitMQ/Kafka) be used?

Yes.

RabbitMQ will be used with Celery for background processing.

Tasks:

* Email notifications
* Analytics updates
* Audit logging
* Report generation

Workflow:

```text
Application Submitted
        |
        V
     RabbitMQ
        |
        V
   Celery Worker
        |
        +--> Send Email
        +--> Update Analytics
```

For this project RabbitMQ is sufficient. Kafka is generally used for large-scale event streaming systems.

---

## 7. How will the system scale?

### Horizontal Scaling

Multiple API servers will run behind a load balancer.

```text
NGINX
  |
--------------------
|        |         |
API-1   API-2    API-3
```

### Database Scaling

* Primary Database for writes
* Read Replicas for read-heavy operations

### Cache Scaling

Redis Cluster can be introduced when traffic increases.

### Containerization

Docker and Kubernetes can be used for automated deployment and scaling.

---

## Conclusion

The platform can efficiently handle high traffic by combining:

* Django DRF
* PostgreSQL
* Redis
* RabbitMQ
* Celery
* Horizontal Scaling
* Proper Database Indexing

This ensures low latency, high availability, and data consistency.
