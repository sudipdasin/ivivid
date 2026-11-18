# iVivid — Open Free + Private Pro strategy

## Decision

**Public upstream:** `sudipdasin/ivivid` stays MIT-licensed and independently useful. Community contributors can fork, build, and distribute the Free edition. **Private downstream (proposed):** `sudipdasin/ivivid-pro-private`, a separate GitHub **private** repository, carries the Free upstream as an upstream remote plus new proprietary code in `proprietary/`. This private repository DOES NOT EXIST until explicitly created and its visibility verified. No private source should ever be committed to the public repository, even temporarily.

### Trust boundary

- Public: `iVivid.py` (existing legacy entry point), `ivivid_core/`, public docs, tests, packaging, and `tools/check_public_boundary.py`.
- Private only: `proprietary/` implementations, paid algorithms, commercial assets, licensing integration, billing, private test fixtures, signing keys, and customer entitlements. Store actual secrets in a secrets manager, **not in either Git repository**.
- Share only **data contracts** (versioned `ExtensionManifest` and `Capability` declarations) in public. Never add private imports to Free. Pro distribution must be assembled from the private checkout; public artifacts are built from public checkout only.
- The public MIT license is preserved. Already published MIT code cannot retroactively be made proprietary; new privately authored modules can be licensed separately. Review rights to community contributions and third-party shader licenses before commercial distribution.

### Sync policy

**One-way public -> private**, not two-way. The private checkout tracks public `main` via an `upstream` remote. Pull reviewed public changes into private; do not push private branch to public. Automatic bidirectional mirroring is forbidden because it could leak proprietary source. Rebase/merge strategy is decided by maintainers; never overwrite a private branch with `reset --hard`. Sync can be automated *only inside the private repository* after branch protections and secret scanning are configured.

Example for a maintainer, after creating the private repo in GitHub UI and checking visibility:

```sh
# Start from a PRIVATE clone of the new private repo; verify its remote URL first.
git remote add upstream https://github.com/sudipdasin/ivivid.git
git fetch upstream main
git switch -c sync/public-main
# Review changes and merge into a private integration branch; no automatic push to public.
git merge --no-ff upstream/main
# Open a PR within the private repository; run private CI and review before merge.
```

### Proposed differentiators (not yet implemented)

1. **Adaptive Frame Budgeter:** measure playback frame-time and select an enhancement chain under a target latency budget, with per-device calibration.
2. **Scene-aware Tone Mapping:** detect dark/bright scene changes locally and smoothly adjust enhancement strength without flicker.
3. **Audio Clarity Profiles:** dialog-focused multiband audio treatment with listening-level safety controls.
4. **Personal Playback Lab:** reproducible A/B comparison, perceptual preference tuning, exportable device profiles.
5. **Multi-device Profile Vault:** encrypted optional sync and conflict resolution; local-only mode remains available.

These are product ideas, **not claims of implemented or market-exclusive capabilities**. Research patents, codecs, licenses, privacy and benchmark feasibility before marketing.

### Monetization principles

Keep Free functional with its existing presets and local configuration, without ads or forced account creation. Pro adds independently developed convenience and intelligence, not artificial degradation of Free. Publish a clear feature matrix and pricing later; no payment or activation system is implemented now. Commercial release requires licensing/privacy/security review and a real build pipeline.

### Launch gates

1. Create the private repository and verify `private: true` using authenticated GitHub access.
2. Configure private-only collaborators, protected branches, secret scanning and access policies.
3. Add proprietary code *only after* private visibility is confirmed.
4. Implement a one-way upstream sync PR workflow in the private repo, with explicit review.
5. Validate Free installation, Pro packaging, dependencies, license notices, and the public-boundary guard independently.
6. Confirm both editions can be built without cross-contaminating release artifacts.

No private repo, Pro feature, licensing system, release, or paid product is claimed to exist today.
