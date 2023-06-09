module.exports = {
	root: true,
	env: {
		node: true
	},
	extends: ['plugin:vue/essential', 'eslint:recommended'],
	rules: {
		'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
		'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
		'no-empty-pattern': 'off',
		'no-unused-vars': 'warn',
		'vue/multi-word-component-names': 'warn',
	},
	parserOptions: {
		parser: 'babel-eslint'
	}
}
