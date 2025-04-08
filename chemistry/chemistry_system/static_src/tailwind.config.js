/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        '../templates/**/*.html',
        '../templates/**/cotton/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {},
        screens: {
            sm: '640px',
            md: '768px',
            lg: '1024px',
            xl: '1280px',
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('daisyui'),
    ],
    daisyui: {
        themes: ["light", "dark"],
    },
};
