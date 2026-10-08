# Scientific data layout

The corpus separates causal model definitions from generated samples.

`causal_agents/catalog`: validated model-family records.
`causal_agents/schemas`: serialized schema/version information.
`causal_agents/provenance`: source-to-equation provenance manifests.
`generated/raw`: raw outputs.
`generated/validated`: outputs that passed validation.
`generated/processed`: derived feature tables.
`metadata`: configurations, environment captures and hashes.

Large generated datasets should not be committed by default. Prefer CI artifacts
or versioned releases with reproducibility metadata.
