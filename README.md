# Asynchronous Framework Demo

- [如何在架构层面解决90%的问题【让编程再次伟大#12】](https://www.youtube.com/watch?v=Y0688p1afBo)

```mermaid
graph LR
    User((User)) -->|HTTP| GraphQL[GraphQL]
    GraphQL -->|SQL| PostgreSQL[(PostgreSQL)]
    PostgreSQL -->|trigger| Worker1[worker]
    PostgreSQL -->|trigger| Worker2[worker]
    PostgreSQL -->|trigger| Worker3[worker]
    PostgreSQL -->|trigger| Worker4[worker]
    
    Worker1 -.->|3rd party API| API[Third Party API]
    Worker2 -.->|3rd party API| API
    Worker3 -.->|3rd party API| API
    Worker4 -.->|3rd party API| API
    
    subgraph Sync[Synchronous]
        User
        GraphQL
        PostgreSQL
    end
    
    subgraph Async[Asynchoronous]
        Worker1
        Worker2
        Worker3
        Worker4
        API
    end
    
    classDef orange fill:#ff6600,stroke:#fff,stroke-width:2px,color:#fff
    classDef database fill:#ff9966,stroke:#fff,stroke-width:2px,color:#fff
    classDef user fill:#ff9966,stroke:#fff,stroke-width:2px,color:#000
    
    class GraphQL,Worker1,Worker2,Worker3,Worker4 orange
    class PostgreSQL database
    class User user
```

```txt
Client ─HTTP/GraphQL─► PostgreSQL
                              │ (trigger + pg_notify)
                              ▼
                        LISTEN/NOTIFY
                              │
                 Worker(s) ───┘──► 第三方 API
```

## Todo

- [ ] Backend-end demo
- [ ] PostgreSQL (use Supabase) with trigger and notification
- [ ] Front-end to submit task using GraphQL
