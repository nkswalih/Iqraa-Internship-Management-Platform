# Section D - Query Optimization

## Given Query

```sql
SELECT *
FROM applications
WHERE internship_id = 100
ORDER BY created_at DESC;
```

The applications table contains more than 10 million records.

---

## 1. Why is the query slow?

Without proper indexes, PostgreSQL performs a Full Table Scan.

This means:

* Every row must be inspected.
* The database must sort matching rows by created_at.
* Large amounts of disk I/O occur.

With 10+ million records, this results in significant execution time.

---

## 2. How will the query be optimized?

### Avoid SELECT *

Only retrieve the required columns.

```sql
SELECT
    id,
    student_id,
    status,
    created_at
FROM applications
WHERE internship_id = 100
ORDER BY created_at DESC;
```

### Add Pagination

```sql
SELECT
    id,
    student_id,
    status,
    created_at
FROM applications
WHERE internship_id = 100
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

This reduces the amount of data returned by the database.

---

## 3. What indexes will be created?

### Basic Index

```sql
CREATE INDEX idx_application_internship
ON applications(internship_id);
```

This speeds up filtering by internship_id.

### Composite Index

```sql
CREATE INDEX idx_application_internship_created
ON applications(
    internship_id,
    created_at DESC
);
```

Benefits:

* Fast filtering
* Fast ordering
* Reduced sorting overhead

This is the preferred solution.

---

## 4. How will performance improvement be measured?

Use PostgreSQL EXPLAIN ANALYZE.

Before optimization:

```sql
EXPLAIN ANALYZE
SELECT *
FROM applications
WHERE internship_id = 100
ORDER BY created_at DESC;
```

After optimization:

```sql
EXPLAIN ANALYZE
SELECT
    id,
    student_id,
    status,
    created_at
FROM applications
WHERE internship_id = 100
ORDER BY created_at DESC;
```

Metrics to compare:

* Execution Time
* Planning Time
* Rows Scanned
* Query Cost

Expected Result:

* Full Table Scan → Index Scan
* Seconds → Milliseconds
* Reduced CPU and I/O usage

---

## Conclusion

Query performance can be significantly improved by:

* Creating proper indexes
* Using composite indexes
* Avoiding SELECT *
* Implementing pagination
* Monitoring execution plans using EXPLAIN ANALYZE

These optimizations ensure efficient query execution even with tens of millions of records.
