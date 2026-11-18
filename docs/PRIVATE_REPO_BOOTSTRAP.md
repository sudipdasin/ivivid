# Private iVivid Pro repository bootstrap

Create `sudipdasin/ivivid-pro-private` using GitHub's **Private** visibility option. Do not import any proprietary code before confirming the repository API returns `private: true`. Use a separate private clone, with the public repo as read-only upstream. Keep `proprietary/`, private fixtures, commercial plans, and build signing configuration in the private repository only. Set branch protections and require code review. Enable secret scanning where available. Use a one-way pull/PR from public to private; never mirror private to public. Check release artifacts and source distributions for proprietary modules before publishing Free. A GitHub private repo is access-controlled, not a substitute for encryption or key management.

**Note:** The public repository contains only architecture/contracts and no proprietary feature implementation. A private repository has not been created by this change.
