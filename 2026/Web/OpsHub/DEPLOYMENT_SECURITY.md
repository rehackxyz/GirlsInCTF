# Shared deployment boundary

The `ops` Compose network is marked `internal`; metadata and deploy are attached
only to that network and have no published ports. Edge is dual-homed on `ops`
and a separate ingress bridge, with its challenge port published to the host.
The services also use read-only root filesystems, with a small temporary
filesystem for `/tmp`.

The edge allowlist limits application fetches to the two intended backends, but
the ingress bridge gives edge an external route. Apply host-level egress rules
to deny edge arbitrary outbound access as defense in depth. `internal: true` on
`ops` is not a substitute for host firewall policy: depending on the Docker host
and its routes, containers may still reach the bridge gateway or host services.
Apply host-level rules to the OpsHub bridge interface and subnet so containers
cannot reach host management services or other internal networks. Compose
cannot express or verify those host-specific rules.

The edge port mapping binds to `127.0.0.1` by default for a host reverse proxy.
Set `CHALLENGE_BIND_IP=0.0.0.0` only when the platform requires direct access to
the published challenge port. Docker warns that publishing without a host IP binds
all interfaces and may bypass host firewall rules; Compose cannot define the host's
ingress policy.

The application gives each successful login a separate draft owner and caps
drafts per owner. This reduces cross-login state access in a shared instance,
but does not provide per-team process, network, or availability isolation. Use
one deployment per team when teams require stronger isolation, separate secrets,
or independent resource limits.

Drafts and their caps are in-memory, so keep deploy at its current single
worker and single container. Horizontal scaling requires shared transactional
draft storage and atomic cap enforcement. The edge signing key is generated at
startup; the current preloaded Gunicorn master shares it across its workers,
but multiple edge containers need a shared configured signing secret.
