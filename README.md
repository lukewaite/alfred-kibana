# Alfred Kibana

Quickly navigate to Kibana Saved Searches in [Alfred 3][alfred].

![][sample]

## Setup and Usage
* Tell it where the Kibana API you want to connect to is by running `logseturl http://my-kibana-host.com`
* search for saved searches with `logs <search>`

## Notes
The Kibana server I use day to day is behind a VPN, but not fronted by any other authentication, so this workflow
does not handle any of the Elastic or alternative authentication methods available.

Tested against Kibana 5.6.

## TODOs
* Initial release.

# Thanks, License, Copyright

- The [Alfred-Workflow][alfred-workflow] library is used heavily, and it's wonderful documentation was key in building the plugin.
- The Kibana icon is used, care of Elastic.

All other code/media are released under the [MIT Licence][license].

[alfred]: http://www.alfredapp.com/
[alfred-workflow]: http://www.deanishe.net/alfred-workflow/
[license]: src/LICENSE.txt
[sample]: https://raw.github.com/lukewaite/alfred-kibana/master/docs/sample.jpg