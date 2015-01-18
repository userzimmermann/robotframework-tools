# robotframework-tools
#
# Python Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013-2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# robotframework-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# robotframework-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with robotframework-tools. If not, see <http://www.gnu.org/licenses/>.

"""robottools.library.session.metaoptions

testlibrary()'s session handler meta options management.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Meta']

from moretools import camelize, decamelize


class Meta(object):
    """The meta options manager for :class:`.SessionHandler`.

    - Based on the handler's class name
      and a user-defined `Handler.Meta` class.
    """
    def __init__(self, handlerclsname=None, options=None):
        """Generate several variants of a session handler name
           for use in identifiers and message strings.

        - Based on the `handlerclsname`
          and/or the attributes of the optional
          `Handler.Meta` class in `options`,
          which can define name (variant) prefixes/suffixes
          and/or explicit name variants.
        """
        # Check all prefix definitions and generate actual prefix strings
        prefixes = {}

        def gen_prefix(key, default, append=''):
            """Check the prefix definition
               for name variant identified by `key`.

            - Set to `default` if not defined.
            - Always `append` the given extra string.
            """
            try:
                prefix = getattr(
                  options, (key and key + '_') + 'name_prefix')
            except AttributeError:
                prefix = default
            else:
                prefix = prefix and str(prefix) or ''
            if prefix and not prefix.endswith(append):
                prefix += append
            # Finally add to the prefixes dictionary
            prefixes[key] = prefix

        def gen_plural_prefix(key, append=''):
            """Check the prefix definition
               for plural name variant identified by plural_`key`.

            - Set to singular `key` prefix if not defined.
            - Always `append` the given extra string.
            """
            plural_key = 'plural' + (key and '_' + key)
            default = prefixes[key]
            gen_prefix(plural_key, default, append)

        # Base name prefixes
        gen_prefix('', '', '_')
        gen_plural_prefix('', '_')
        gen_prefix('upper', camelize(prefixes['']))
        gen_plural_prefix('upper')
        # Identifier name prefixes
        gen_prefix('identifier', '', '_')
        gen_plural_prefix('identifier', '_')
        gen_prefix('upper_identifier', camelize(prefixes['identifier']))
        # Verbose name prefixes
        gen_prefix('verbose', '', ' ')
        gen_plural_prefix('verbose', ' ')

        # Check all suffix definitions and generate actual suffix strings
        suffixes = {}

        def gen_suffix(key, default, prepend=''):
            """Check the suffix definition
               for name variant identified by `key`.

            - Set to `default` if not defined.
            - Always `prepend` the given extra string.
            """
            try:
                suffix = getattr(options, key + '_name_suffix')
            except AttributeError:
                suffix = default
            else:
                suffix = suffix and str(suffix) or ''
            if suffix and not suffix.startswith(prepend):
                suffix = prepend + suffix
            # Finally add to the suffixes dictionary
            suffixes[key] = suffix

        def gen_plural_suffix(key, prepend=''):
            """Check the suffix definition
               for plural name variant identified by plural_`key`.

            - Set to singular `key` suffix + 's' if not defined.
            - Always `prepend` the given extra string.
            """
            plural_key = 'plural' + (key and '_' + key)
            default = suffixes[key] and suffixes[key] + 's'
            gen_suffix(plural_key, default, prepend)

        # Identifier name suffixes
        gen_suffix('', '', '_')
        gen_plural_suffix('', '_')
        gen_suffix('upper', camelize(suffixes['']))
        gen_plural_suffix('upper')
        # Identifier name suffixes
        ## gen_suffix('identifier', 'session', '_')
        gen_suffix('identifier', '', '_')
        gen_plural_suffix('identifier', '_')
        gen_suffix('upper_identifier', camelize(suffixes['identifier']))
        # Verbose name suffixes
        ## gen_suffix('verbose', 'Session', ' ')
        gen_suffix('verbose', '', ' ')
        gen_plural_suffix('verbose', ' ')

        # Check explicit name variant definitions
        variants = {}
        for variantkey in (
          '', 'plural', 'upper', 'plural_upper',
          'identifier', 'plural_identifier', 'upper_identifier',
          'verbose', 'plural_verbose'
          ):
            defname = (variantkey and variantkey + '_') + 'name'
            variant = getattr(options, defname, None)
            # Non-empty string or None
            variant = variant and (str(variant) or None) or None
            variants[variantkey] = variant

        # Create final base name (helper) variants
        # (NOT stored in final meta object (self))
        key = ''
        name = (
          variants[key]
          or prefixes[key] + decamelize(handlerclsname) + suffixes[key])
        key = 'plural'
        plural_name = (
          variants[key] and prefixes[key] + variants[key] + suffixes[key]
          or None)
        key = 'upper'
        upper_name = (
          variants[key]
          or variants[''] and camelize(variants[''])
          or prefixes[key] + handlerclsname + suffixes[key])
        key = 'plural_upper'
        plural_upper_name = (
          variants[key]
          or variants['plural']
          and prefixes[key] + camelize(variants['plural']) + (
            suffixes[key] or (not variants['plural'] and 's' or ''))
          or None)

        # Create final identifier/verbose name variants
        # (stored in final meta object (self))
        key = 'identifier'
        self.identifier_name = (
          variants[key]
          or prefixes[key] + name + suffixes[key])
        key = 'plural_identifier'
        self.plural_identifier_name = (
          variants[key]
          or prefixes[key] + (plural_name or name) + (
            suffixes[key] or (not plural_name and 's' or '')))
        key = 'upper_identifier'
        self.upper_identifier_name = (
          variants[key]
          or prefixes[key] + upper_name + suffixes[key])
        key = 'verbose'
        self.verbose_name = (
          variants[key]
          or prefixes[key] + upper_name + suffixes[key])
        key = 'plural_verbose'
        self.plural_verbose_name = (
          variants[key]
          or prefixes[key] + (plural_upper_name or upper_name) + (
            suffixes[key] or (not plural_upper_name and 's' or '')))

