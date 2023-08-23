# Running libraries locally

There are two libraries (out of many that `admin` depends on), which can be run locally for development purposes.

These are:

* `govuk-frontend` - npm package
* `govuk-frontend-jinja` - python package

## Working locally with `govuk-frontend` package

When working locally with `govuk-frontend` package, add in `package.json` the path to local package:

```
"govuk-frontend": "file:///replace_with_absolute_path_to/govuk-frontend/package/",
```

After each build of `govuk-frontend`:
1. Run `npm install` in case a file has been added to/removed from the `govuk-frontend`. Sometimes, the changes don't get picked up without running `install`
1. Run `npm run build` to rebuild the styles for the `admin`
1. Run the app with `make run-flask`

## Working locally with `govuk-frontend-jinja`

After each build of `govuk-frontend-jinja`, force reinstall the package with the local version:

```
pip install /absolute/path/to/govuk-frontend-jinja/dist/govuk_frontend_jinja-2.3.0-py3-none-any.whl --force-reinstall
```

Run the app with `make run-flask`.