# Citation

If FED-LINk helped you — in a paper, a talk, a course, or a repo you built
on top of it — here's how to cite it. There is no DOI; cite the repository.

## Preferred citation formats

**BibTeX:**

```bibtex
@software{fedlink2026,
  author  = {fedpromptly},
  title   = {{FED-LINk}: A Build-Time URL Shortener for Static Hosting},
  year    = {2026},
  url     = {https://github.com/fedpromptly/infinityfree-shortener-builder},
  note    = {Version 1.1.0},
  license = {MIT}
}
```

**APA:**

> fedpromptly. (2026). *FED-LINk: A build-time URL shortener for static
> hosting* (Version 1.1.0) [Computer software].
> https://github.com/fedpromptly/infinityfree-shortener-builder

**IEEE:**

> fedpromptly, "FED-LINk: A build-time URL shortener for static hosting,"
> version 1.1.0. [Software]. GitHub repository. Available:
> https://github.com/fedpromptly/infinityfree-shortener-builder

**Plain text:**

> FED-LINk — a build-time URL shortener for static hosting, by
> fedpromptly, version 1.1.0, MIT license.
> https://github.com/fedpromptly/infinityfree-shortener-builder

## Citing a specific version

Releases are tagged `vX.Y.Z` — see the GitHub Releases page and
[`CHANGELOG.md`](CHANGELOG.md) for what changed in each. Swap the version
in the examples above for the tag you actually used, and prefer the tag's
commit SHA over `main` for reproducibility:

```bibtex
@software{fedlink2026v100,
  author = {fedpromptly},
  title  = {{FED-LINk}: A Build-Time URL Shortener for Static Hosting},
  year   = {2026},
  url    = {https://github.com/fedpromptly/infinityfree-shortener-builder/releases/tag/v1.0.0},
  note   = {Version 1.0.0, exact release tag}
}
```

## If you fork or build on it

MIT requires the copyright notice travel with the code — keep the
[`LICENSE`](LICENSE) file and credit the upstream in your README (one line
is fine: "Based on FED-LINk by fedpromptly"). A citation in academic work
is not legally required, but it is the decent thing and helps others find
the approach.

## Related concepts worth citing alongside

The architecture leans on well-known ideas, if you want to cite them too:

- Apache `mod_alias` `Redirect` directives and `.htaccess` — the Apache
  HTTP Server documentation, https://httpd.apache.org/docs/
- Static-site generation as a deployment model — any standard static
  site generator literature
- HTTP `301 Moved Permanently` semantics — RFC 9110, Section 15.4.2,
  https://www.rfc-editor.org/rfc/rfc9110
- GitHub Actions build pipelines — GitHub documentation,
  https://docs.github.com/actions
