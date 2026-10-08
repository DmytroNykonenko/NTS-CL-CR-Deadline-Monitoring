# NTS Report Deadline Monitoring

Static GitHub Pages dashboard with scheduled ArcGIS Online data export.

## Security
The exported `data/nts.json` is PUBLIC when deployed to GitHub Pages. Only deploy if publication of report IDs, dates and statuses is authorized. Do not put ArcGIS credentials in repository files. GitHub Actions secrets are not exposed to Pages, but exported data is.

## Setup
1. Create a GitHub repository and upload these files.
2. Add repository Actions secrets `AGOL_USERNAME`, `AGOL_PASSWORD` and `AGOL_PORTAL` (`https://www.arcgis.com`). Prefer a dedicated read-only account. Password-based automation may be incompatible with your organization's SSO/MFA policy; if so, use a supported server-to-server OAuth flow instead.
3. Configure Actions variable `AGOL_LAYER_URL` with the exact feature layer REST URL (ending `/FeatureServer/0` or the correct sublayer index). The item ID alone does not determine the layer index.
4. Run **Actions → Update NTS data → Run workflow** and confirm `data/nts.json` is populated.
5. Enable **Settings → Pages → Deploy from a branch → main / root**.
6. By default the workflow runs every 15 minutes; scheduled GitHub Actions may be delayed.

## Deadline rules
`end_dt` is the starting date and is not counted. Add 10 weekdays, excluding Saturday and Sunday. `Approved` is `Submitted` regardless of deadline. Other statuses are computed in the browser against the current local calendar date. Holidays are not excluded. `Due Soon` means 1–2 working days left.

## Notes
The browser refreshes data every 5 minutes, while the source JSON updates on the workflow schedule. No ArcGIS password/token is sent to the browser. If an update fails, the dashboard displays the last successfully published JSON.
