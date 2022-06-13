'use strict';
var parser = require("solidity-parser-antlr")
var fs = require('fs');
var path = require('path');
var inputAddress = fs.readFileSync('/home/yfliu/paper_code/gasDetect/inputAddress').toString();
inputAddress = inputAddress.slice(0,inputAddress.length-1);
var outputAddress = '/home/yfliu/paper_data/gasPattern/gasDetectResult6.txt'

var filePath = path.resolve(inputAddress);
var countIndex = 0;
var countCompileFail = 0;
var flag = false;

fs.readdir(filePath,function(err,files){
	if(err){
		console.warn(err)
	}else{
		files.forEach(function(fileName){
			console.log("正在处理第 " + ++countIndex + " 个文件 : " + fileName);
			
			// 读取智能合约
			var filedir = path.join(filePath,fileName);
			if (fileName.search(":") != -1){
				return;
			}
			// 解析智能合约
			var address = fileName.replace(/\.sol/g,"");
			var data = fs.readFileSync(filedir);
			var code = data.toString();
			var processedCode = code.replace(/&#39;/g,"\'");

			try{
				var result = parser.parse(processedCode,{loc : true});
			}catch(err){
    			console.error('Failed to parse, ' + address + '\n', err);
    			// fs.appendFileSync('/data/kongqp/gas_optimization/log/compileFail.txt', ++countCompileFail + ' : ' + address + '\r\n');
    			return;
			}


			// fs.appendFileSync(outputAddress, countIndex + ' : ' + address + '\r\n');
			// flag = false;
			if(result.children.length != 0){
				for(var i = 0; i < result.children.length; i++){
					if(result.children[i].type == 'ContractDefinition'){
						fs.appendFileSync(outputAddress, countIndex + ' : ' + address + ' : ' + result.children[i].name + '\r\n');
						flag = false;
						// 将uint8-248/int8-248 替换成uint256/int256
						detectPattern(result.children[i]);
						if(flag == true){
							fs.appendFileSync(outputAddress,"success" + '\r\n');
						}
					}
				}
			}
			// if(flag == true){
			// 	fs.appendFileSync(outputAddress,"success" + '\r\n');
			// }
		});
	}
});


function detectPattern(_AST){
	// 记录变量类型及位置
	preOrderTraversel(_AST);
}

function preOrderTraversel(_AST){
	if(typeof _AST == 'string' || typeof _AST == 'number' || _AST == null){
		return;
	}
	if(_AST instanceof Array){
		// console.log();
	}else{
		if(_AST.hasOwnProperty('type')){
			if(_AST.type == 'VariableDeclaration'){
				if(_AST.typeName != null){
					if(_AST.typeName.type == 'ElementaryTypeName'){
						fs.appendFileSync(outputAddress, _AST.typeName.name + " : " + _AST.typeName.loc.start.line + ", " + _AST.typeName.loc.end.line + '\r\n');
						flag = true;
					}
				}
			}
		}
	}
	for(var key in _AST){
		preOrderTraversel(_AST[key]);	
	}
}