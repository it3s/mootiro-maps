// -------------------------------------------------------------------
// markItUp!
// -------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// -------------------------------------------------------------------
// MarkDown tags example
// http://en.wikipedia.org/wiki/Markdown
// http://daringfireball.net/projects/markdown/
// -------------------------------------------------------------------
// Feel free to add more tags
// -------------------------------------------------------------------
mySettings = {
	previewParserPath:	'/markitup/preview/',
	onShiftEnter:		{keepDefault:false, openWith:'\n\n'},
	markupSet: [
		{name:'Título (1o nível)', key:'1', placeHolder:'Seu título aqui...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '=') } },
		{name:'Título (2o nível)', key:'2', placeHolder:'Seu título aqui...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '-') } },
		{name:'Título (3o nível)', key:'3', openWith:'### ', placeHolder:'Seu título aqui...' },
		{name:'Título (4o nível)', key:'4', openWith:'#### ', placeHolder:'Seu título aqui...' },
		{name:'Título (5o nível)', key:'5', openWith:'##### ', placeHolder:'Seu título aqui...' },
		{name:'Título (6o nível)', key:'6', openWith:'###### ', placeHolder:'Seu título aqui...' },
		{separator:'---------------' },
		{name:'Negrito', key:'B', openWith:'**', closeWith:'**'},
		{name:'Itálico', key:'I', openWith:'_', closeWith:'_'},
		{separator:'---------------' },
		{name:'Lista não-ordenada', openWith:'- ' },
		{name:'Lista ordenada', openWith:function(markItUp) {
			return markItUp.line+'. ';
		}},
		{separator:'---------------' },
		{name:'Image', key:'P', replaceWith:'![[![Alternative text]!]]([![Url:!:http://]!] "[![Title]!]")'},
		{name:'Link', key:'L', openWith:'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder:'Seu texto para linkar aqui...' },
		{separator:'---------------'},
		{name:'Citação', openWith:'> '},
		{name:'Código', openWith:'(!(\t|!|`)!)', closeWith:'(!(`)!)'},
		{separator:'---------------'},
		{name:'Visualização Prévia', call:'preview', className:"preview"}
	]
}

// mIu nameSpace to avoid conflict.
miu = {
	markdownTitle: function(markItUp, char) {
		heading = '';
		n = $.trim(markItUp.selection||markItUp.placeHolder).length;
		// work around bug in python-markdown where header underlines must be at least 3 chars
		if (n < 3) { n = 3; }
		for(i = 0; i < n; i++) {
			heading += char;
		}
		return '\n'+heading;
	}
}
