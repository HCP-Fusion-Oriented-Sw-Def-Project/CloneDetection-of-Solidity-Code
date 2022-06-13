'use strict';
// var parser = require("solidity-parser-antlr");
var parser = require("solidity-parser-diligence");
var fs = require('fs');
var path = require('path');
var inputAddress = fs.readFileSync('/home/yfliu/paper_code/gasDetect/inputAddress').toString();
inputAddress = inputAddress.slice(0,inputAddress.length-1);
var outputAddress = '/home/yfliu/paper_data/gasPattern/gasDetectResult4.txt'
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

/*
			fs.appendFileSync(outputAddress, countIndex + ' : ' + address + '\r\n');
			flag = false;*/
			if(result.children.length != 0){
				for(var i = 0; i < result.children.length; i++){
					if(result.children[i].type == 'ContractDefinition'){
						fs.appendFileSync(outputAddress, countIndex + ' : ' + address + ' : ' + result.children[i].name + '\r\n');
						flag = false;
						detectPattern(result.children[i]);
						if(flag == true){
							fs.appendFileSync(outputAddress,"success" + '\r\n');
						}
					}
				}
			}
			/*
			if(flag == true){
				fs.appendFileSync(outputAddress,"success" + '\r\n');
			}*/
		});
	}
});


function detectPattern(_AST){
	global.stateVariableNames = [];
	for(var i = 0; i < _AST.subNodes.length; i++){
		if(_AST.subNodes[i].type == 'StateVariableDeclaration'){
			stateVariableNames.push(_AST.subNodes[i].variables[0].name);
		}
	}
	for(var i = 0; i < _AST.subNodes.length; i++){
		preOrderTraversel(_AST.subNodes[i]);
	}
}

function preOrderTraversel(_AST){
	if(typeof _AST == 'string' || typeof _AST == 'number' || _AST == null){
		return;
	}
	if(_AST instanceof Array){
		// console.log();
	}else{
		if(_AST.hasOwnProperty('type')){
			if(_AST.type == 'BinaryOperation'){
				if(_AST.operator == '&&' || _AST.operator == '||' ){
					var left = tokenizeExpression(_AST.left);
					var right = tokenizeExpression(_AST.right);
					if(compareGasCost(left, right)){
						fs.appendFileSync(outputAddress,  "Left : " + _AST.left.loc.start.line  + ", " + _AST.left.loc.end.line  + '\r\n');
						fs.appendFileSync(outputAddress,  "Right : " + _AST.right.loc.start.line  + ", " + _AST.right.loc.end.line  + '\r\n');
						flag = true;
						return;
					}
				}
			}
		}
	}
	for(var key in _AST){
		preOrderTraversel(_AST[key]);
	}
}

function compareGasCost(_tokens1, _tokens2){
	var difference = (getGasCost(_tokens1) - getGasCost(_tokens2));
	if(difference > 50){
		return true;
		// fs.appendFileSync('/data/kongqp/gas_optimization/log/pattern2.txt', "yes : " + difference + '\r\n');
	}else{
		return false;
	}
}

function getGasCost(_tokens){
	var gasCost = 0;
	for(var i = 0; i < _tokens.length; i++){
		switch(_tokens[i]){
			case 'FunctionCall':
				gasCost += 200;
			case 'Balance':
				gasCost += 400;
			case 'SLOAD':
				gasCost += 200;
			default:
				gasCost += 3;
		}
	}
	return gasCost;
}


function tokenizeExpression(_AST){
	switch(_AST.type){
		case 'FunctionCall':
			return tokenizeFunctionCall(_AST);
		case 'BinaryOperation':
			return tokenizeBinaryOperation(_AST);
		case 'UnaryOperation':
			return tokenizeUnaryOperation(_AST);
		case 'Identifier':
			return tokenizeIdentifier(_AST);
		case 'IndexAccess':
			return tokenizeIndexAccess(_AST);
		case 'MemberAccess':
			return tokenizeMemberAccess(_AST);
		case 'ElementaryTypeNameExpression':
			return tokenizeElementaryTypeNameExpression(_AST);
		case 'NewExpression':
			return tokenizeNewExpression(_AST);
		case 'TupleExpression':
			return tokenizeTupleExpression(_AST);
		case 'BooleanLiteral':
			return tokenizeBooleanLiteral(_AST);
		case 'NumberLiteral':
			return tokenizeNumberLiteral(_AST);
		case 'StringLiteral':
			return tokenizeStringLiteral(_AST);
		case 'Conditional':
			return tokenizeConditional(_AST);
		case 'HexNumber':
			return tokenizeHexNumber(_AST);
		case 'DecimalNumber':
			return tokenizeDecimalNumber(_AST);
		case 'AssemblyCall':
			return tokenizeAssemblyCall(_AST);
		case 'HexLiteral':
			return tokenizeHexLiteral(_AST);
		default:
        	return [];
	}

}

function tokenizeFunctionCall(_AST){
	var tokenSequence = ['FunctionCall'];
	var tempTokenSequence = tokenizeExpression(_AST.expression);
	for(var i=0; i < tempTokenSequence.length; i++){
		tokenSequence.push(tempTokenSequence[i]);
	}
	if(_AST.arguments.length != 0){
		tempTokenSequence = tokenizeArguments(_AST.arguments);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	return tokenSequence;
}

function tokenizeArguments(_AST){
	var tokenSequence = [];
	var tempTokenSequence;
	for(var i = 0; i < _AST.length; i++){
		tempTokenSequence = tokenizeExpression(_AST[i]);
		for(var j=0; j < tempTokenSequence.length; j++){
			tokenSequence.push(tempTokenSequence[j]);
		}
	}
	return tokenSequence;
}

function tokenizeBinaryOperation(_AST){
	var tokenSequence = ['BinaryOperation'];
	var tempTokenSequence;
	if(_AST.left != null){
		tempTokenSequence = tokenizeExpression(_AST.left);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	if(_AST.right != null){
		tempTokenSequence = tokenizeExpression(_AST.right);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	return tokenSequence;
}

function tokenizeUnaryOperation(_AST){
	var tokenSequence = ['UnaryOperation'];
	if(_AST.subExpression != null){
		var tempTokenSequence = tokenizeExpression(_AST.subExpression);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	return tokenSequence;
}

function tokenizeIdentifier(_AST){
	if(stateVariableNames.indexOf(_AST.name) != -1){
		return ["SLOAD"];
	}else{
		return ['Identifier'];
	}
}

function tokenizeIndexAccess(_AST){
	var tokenSequence = ['IndexAccess'];
	var tempTokenSequence;
	if(_AST.base != null){
		tempTokenSequence = tokenizeExpression(_AST.base);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	if(_AST.index != null){
		tempTokenSequence = tokenizeExpression(_AST.index);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	return tokenSequence;
}

function tokenizeMemberAccess(_AST){
	var tokenSequence = ['MemberAccess'];
	var tempTokenSequence = tokenizeExpression(_AST.expression);
	for(var i=0; i < tempTokenSequence.length; i++){
		tokenSequence.push(tempTokenSequence[i]);
	}
	if(_AST.memberName == 'balance'){
		tokenSequence.push("Balance")
	}
	return tokenSequence;
}

function tokenizeElementaryTypeNameExpression(_AST){
	var tokenSequence = ['ElementaryTypeNameExpression'];
	if(_AST.typeName != null){
		var tempTokenSequence = tokenizeTypeName(_AST.typeName);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
    return tokenSequence;
}

function tokenizeTypeName(_AST){
	switch(_AST.type){
		case 'ArrayTypeName':
			return tokenizeArrayTypeName(_AST);
		case 'ElementaryTypeName':
			return tokenizeElementaryTypeName(_AST);
		case 'UserDefinedTypeName':
			return tokenizeUserDefinedTypeName(_AST);
		case 'Mapping':
			return tokenizeMapping(_AST);
		case 'FunctionTypeName':
			return tokenizeFunctionTypeName(_AST);
		case 'ImportDirective':
			return tokenizeImportDirective(_AST);
		default:
        	return [];
	}
}

function tokenizeArrayTypeName(_AST){
	var tokenSequence = ['ArrayTypeName'];
	var tempTokenSequence;
	if(_AST.baseTypeName != null){
		tempTokenSequence = tokenizeTypeName(_AST.baseTypeName);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	if(_AST.length != null){
		switch(_AST.length.type){
			case 'NumberLiteral':
				tempTokenSequence = tokenizeNumberLiteral(_AST.length);
				break;
			case 'Identifier':
				tempTokenSequence = tokenizeIdentifier(_AST.length);
				break;
			case 'BinaryOperation':
				tempTokenSequence = tokenizeBinaryOperation(_AST.length);
				break;
			default:
				tempTokenSequence = [];
		}
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}

	}
	return tokenSequence;
}

function tokenizeElementaryTypeName(_AST){
	return [_AST.type];
}

function tokenizeUserDefinedTypeName(_AST){
	return [_AST.namePath];
}

function tokenizeMapping(_AST){
	var tokenSequence = ['Mapping'];
	var tempTokenSequence;
	if(_AST.keyType != null){
		tempTokenSequence = tokenizeTypeName(_AST.keyType);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	if(_AST.valueType != null){
		tempTokenSequence = tokenizeTypeName(_AST.valueType);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	return tokenSequence;
}

function tokenizeFunctionTypeName(_AST){
	var tokenSequence = ['FunctionTypeName'];
	var tempTokenSequence;

	if(_AST.parameterTypes.length != 0){
		tempTokenSequence = tokenizeParameters(_AST.parameterTypes);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	// if(_AST.stateMutability != null){
	// 	tokenSequence += (' ' + _AST.stateMutability);
	// }
	// if(_AST.visibility != null){
	// 	tokenSequence += (' ' + _AST.visibility);
	// }
	// if(_AST.returnTypes.length != 0){
	// 	tokenSequence += (' ' + 'returns' + ' ' + '(');
	// 	tokenSequence += (' ' + _AST.visibility);
	// 	tokenSequence += (' ' + ')');
	// }
	return tokenSequence;
}

function tokenizeImportDirective(_AST){
	return ['ImportDirective'];
}

function tokenizeNewExpression(_AST){
	var tokenSequence = ['NewExpression'];
	if(_AST.typeName != null){
		var tempTokenSequence = tokenizeTypeName(_AST.typeName);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
    return tokenSequence;
}

function tokenizeTupleExpression(_AST){
	var tokenSequence = ['TupleExpression'];
	var tempTokenSequence;
	for(var i = 0; i < _AST.components.length; i++){
		tempTokenSequence = tokenizeExpression(_AST.components[i]);
		for(var j=0; j < tempTokenSequence.length; j++){
			tokenSequence.push(tempTokenSequence[j]);
		}
	}
	return tokenSequence;
}

function tokenizeBooleanLiteral(_AST){
	return ['BooleanLiteral'];
}

function tokenizeNumberLiteral(_AST){
	return ["NumberLiteral"];
}

function tokenizeStringLiteral(_AST){
	return ["StringLiteral"];
}

function tokenizeConditional(_AST){
	var tokenSequence = ['Conditional'];
	var tempTokenSequence;
	if(_AST.condition != null){
		tempTokenSequence = tokenizeExpression(_AST.condition);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	if(_AST.trueExpression != null){
		tempTokenSequence = tokenizeExpression(_AST.trueExpression);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	if(_AST.falseExpression != null){
		tempTokenSequence = tokenizeExpression(_AST.falseExpression);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
    return tokenSequence;
}

function tokenizeHexNumber(_AST){
	return ['HexNumber'];
}

function tokenizeDecimalNumber(_AST){
	return ['DecimalNumber'];
}

function tokenizeAssemblyCall(_AST){
	var tokenSequence = ['AssemblyCall'];
	if(_AST.arguments.length != 0){
		var tempTokenSequence = tokenizeArguments(_AST.arguments);
		for(var i=0; i < tempTokenSequence.length; i++){
			tokenSequence.push(tempTokenSequence[i]);
		}
	}
	return tokenSequence;
}

function tokenizeHexLiteral(_AST){
	return ["HexLiteral"];
}