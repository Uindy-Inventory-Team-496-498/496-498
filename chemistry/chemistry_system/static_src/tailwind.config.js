/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        // Templates within the chemistry_system app
        '../templates/**/*.html',

        // Main templates directory of the project (if applicable)
        '../../templates/**/*.html',

        // Templates in other Django apps
        '../../**/templates/**/*.html',

        // Uncomment the following lines if you use Tailwind classes in JavaScript or Python
        // '../../**/*.js',
        // '../../**/*.py',
    ],
    theme: {
        extend: {},
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('daisyui'), // Add DaisyUI plugin
    ],
    daisyui: {
        themes: ["light", "dark"], // Optional: Configure DaisyUI themes
    },
}
