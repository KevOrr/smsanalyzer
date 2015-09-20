SMS Analyzer
============

The goal of this side-project is to be able to take an Android mmssms.db
file and abstract it into easy-to-use generic python objects and provide
analytical tools to summarize and visualize various properties of conversations.

Currently, the only database format that it accepts is a [Textra][Textra] mmssms.db file.
If you want smsanalyzer to work with other messaging applications' databases,
then the temporary solution is to download Textra and use the mmssms.db file
that it generates with smsanalyzer.
Or, fork this project and submit a pull request to add models for other sources
of messaging data.

[Textra]: https://play.google.com/store/apps/details?id=com.textra
