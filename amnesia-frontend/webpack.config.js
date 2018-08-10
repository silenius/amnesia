const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        fetch: ['whatwg-fetch', 'promise-polyfill'],
        tinymce: 'tinymce',
        bbpf: './src/bbpf.js',
        folder_show_default: './src/pages/folder/show/default.js'
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'dist')
    },
    module: {
        rules: [{ 
            test: /\.js$/, 
            exclude: /node_modules/, 
            loader: "babel-loader" 
        }]
    }
};
