---
name: localization-flutter
description: "Localize Flutter apps including Russian and Kazakh: ARB files, ICU plurals, intl formatting, text expansion, RTL, fallback locales, translator notes, pseudo-locale testing. Use when adding languages, fixing untranslated or overflowing strings, plural bugs, or when text is hardcoded."
domain: flutter
---

# Flutter localization

- Use `flutter gen-l10n` with ARB files and `AppLocalizations`; no hardcoded user-visible strings, no string concatenation for sentences.
- Plurals/gender via ICU: Russian needs `one/few/many/other`, Kazakh `one/other`:
```json
"unreadCount": "{count, plural, one{{count} непрочитанное} few{{count} непрочитанных} many{{count} непрочитанных} other{{count} непрочитанных}}"
```
- Dates, numbers, currency via `intl` with the active locale; do not hand-format.
- Allow 30-40% text expansion; avoid fixed widths; test long German/Russian strings and large text scale.
- Fallback locale defined; missing key must not crash. Keep keys semantic (`chat_send_button`) and add translator notes (`@key.description`).
- Check RTL if you support Arabic/Hebrew (`Directionality`, `EdgeInsetsDirectional`).
- Test with pseudo-locale or the longest locale.

## Setup checklist
`pubspec.yaml`: `flutter_localizations` + `intl`, `flutter: generate: true`; `l10n.yaml` (`arb-dir`, `template-arb-file: app_en.arb`, `output-localization-file: app_localizations.dart`); `MaterialApp(localizationsDelegates: AppLocalizations.localizationsDelegates, supportedLocales: AppLocalizations.supportedLocales)`. Keep Kazakh (`kk`) in the supported list and make sure the chosen font supports `Ә Ғ Қ Ң Ө Ұ Ү Һ І`.

## Verify
`flutter gen-l10n` succeeds with no missing keys warnings; switch device language at runtime; test the longest locale at text scale 2.0; golden or widget tests for plural boundaries (0, 1, 2, 5, 11, 21, 22, 25).

## Pitfalls
- Concatenating translated fragments.
- Hardcoding date/number formats.
- Using the device locale for server-side formatting.

## Related
`ui-accessibility`, `flutter-testing`, `html-site-builder` (web i18n and hreflang in `web-performance-seo`).
