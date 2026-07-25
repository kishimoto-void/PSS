# Which should I use?

## Use PSS if...

- You want a lightweight problem specification framework.
- You are using a single LLM or a small number of agents.
- You don't need standardized transport between systems.
- You want to integrate quickly into an existing project.

PSS works as a standalone framework and does not require PLP.

---

## Use PLP if...

- You need long-term maintainability.
- Multiple agents or runtimes exchange structured information.
- You want standardized capsules and interoperable components.
- You expect your system to grow over time.

PLP provides a common architecture, transport protocol, and capsule format that PSS and other specifications can share.

---

## Relationship

```
PSS
 └── Standalone Framework

PLP
 ├── Capsule
 ├── Protocol
 ├── Core
 ├── PSS
 ├── PGRA
 └── Future Specifications
```

PSS can be used independently.

When long-term interoperability and ecosystem compatibility become important, PSS can be transported through PLP Capsules without changing the problem specification itself.
